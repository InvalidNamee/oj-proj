import os
import json
import tempfile
import subprocess
from glob import glob
from datetime import datetime
from typing import List, Tuple
from config import DATA_DIR, DEFAULT_TIME_LIMIT, DEFAULT_MEM_LIMIT_MB, DEFAULT_OUTPUT_LIMIT_KB

class JudgeError(Exception):
    pass

def _run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def _ensure_box(box_id: int) -> str:
    # 初始化/获取 box 目录
    init = _run_cmd(["isolate", f"--box-id={box_id}", "--init"])
    # isolate 把路径写在 stderr（部分版本），也可能没有；但即使没有，我们仍可直接运行 --run。
    # 这里返回空字符串无伤大雅。
    return init.stderr.strip()

def _cleanup_box(box_id: int):
    _run_cmd(["isolate", f"--box-id={box_id}", "--cleanup"])

def _copyin(box_id: int, src: str, dst: str):
    # 把 src 拷贝进沙箱内的 dst
    cp = _run_cmd(["isolate", f"--box-id={box_id}", "--silent",
                   "--copyin", src, dst])
    if cp.returncode != 0:
        raise JudgeError(f"copyin failed: {cp.stderr}")

def _run_in_isolate(
    box_id: int,
    run_cmd: List[str],
    time_limit: float,
    mem_limit_mb: int,
    stdin_file: str = None,
    stdout_file: str = "stdout.txt",
    stderr_file: str = "stderr.txt",
    fsize_kb: int = DEFAULT_OUTPUT_LIMIT_KB
) -> Tuple[int, str, str, str]:
    """
    返回 (exit_code, meta, stdout, stderr)
    meta 是 isolate 产生的 JSON-like 在 meta 文件里（用 --meta 获取）。
    """
    with tempfile.NamedTemporaryFile(prefix="iso_meta_", delete=False) as meta_tmp:
        meta_path = meta_tmp.name
    args = [
        "isolate", f"--box-id={box_id}", "--run",
        f"--time={time_limit}",
        f"--mem={mem_limit_mb * 1024}",  # KB
        f"--fsize={fsize_kb}",
        "--stdout", stdout_file,
        "--stderr", stderr_file,
        "--meta", meta_path,
        "--"
    ] + run_cmd

    if stdin_file:
        # stdin_file 已经在 box 里（通过 copyin），这里只告诉 isolate 用哪个
        args.insert(3, f"--stdin={stdin_file}")

    proc = _run_cmd(args)
    # 读取 stdout/stderr 文件
    out = _run_cmd(["isolate", f"--box-id={box_id}", "--cat", stdout_file])
    err = _run_cmd(["isolate", f"--box-id={box_id}", "--cat", stderr_file])

    # 读取 meta
    meta = ""
    try:
        with open(meta_path, "r") as f:
            meta = f.read()
    finally:
        os.unlink(meta_path)

    return proc.returncode, meta, out.stdout, err.stdout

def _load_testcases(problem_id: int):
    base = os.path.join(DATA_DIR, str(problem_id))
    ins = sorted(glob(os.path.join(base, "*.in")))
    dataset = []
    for in_path in ins:
        name = os.path.splitext(os.path.basename(in_path))[0]
        out_path = os.path.join(base, f"{name}.out")
        if os.path.exists(out_path):
            dataset.append((name, in_path, out_path))
    return dataset

def _normalize(s: str) -> str:
    # 常见比较方式：去除尾随空白，逐行对比
    return "\n".join([line.rstrip() for line in s.rstrip().splitlines()])

def judge_submission(
    box_id: int,
    problem_id: int,
    language: str,
    source_code: str,
    limitations: dict
):
    """
    返回 dict:
      {
        "status": "accepted" | "rejected" | "runtime_error" | "time_limit_exceeded" | ...,
        "score": float,
        "cases": [{name, status, time, message}]
      }
    """
    time_limit = float(limitations.get("maxTime", DEFAULT_TIME_LIMIT))
    mem_mb = int(limitations.get("maxMemory", DEFAULT_MEM_LIMIT_MB))

    tests = _load_testcases(problem_id)
    if not tests:
        return {"status": "rejected", "score": 0, "cases": [], "message": "No testcases"}

    # 准备 isolate
    _ensure_box(box_id)

    # 为每次提交创建临时源文件名
    with tempfile.TemporaryDirectory(prefix=f"judge_{problem_id}_") as tmpdir:
        if language == "python":
            src_host = os.path.join(tmpdir, "main.py")
            with open(src_host, "w") as f:
                f.write(source_code)
            _copyin(box_id, src_host, "main.py")
            run_cmd = ["python3", "main.py"]

        elif language == "cpp":
            # 写源码
            src_host = os.path.join(tmpdir, "main.cpp")
            with open(src_host, "w") as f:
                f.write(source_code)
            _copyin(box_id, src_host, "main.cpp")
            # 在沙箱内编译
            code, meta, out, err = _run_in_isolate(
                box_id,
                run_cmd=["/bin/sh", "-lc", "g++ -O2 -std=c++17 -o main main.cpp"],
                time_limit=10.0, mem_limit_mb=512
            )
            if code != 0:
                _cleanup_box(box_id)
                return {"status": "compile_error", "score": 0, "cases": [], "message": err or out}

            run_cmd = ["./main"]

        else:
            _cleanup_box(box_id)
            return {"status": "rejected", "score": 0, "cases": [], "message": f"Unsupported language: {language}"}

        # 拷贝所有输入文件（便于 --stdin 使用）
        # 注意：只需要把 .in 拷进去，.out 在宿主读对照即可
        for _, in_path, _ in tests:
            _copyin(box_id, in_path, os.path.basename(in_path))

        results = []
        passed = 0

        for name, in_path, out_path in tests:
            stdin_name = os.path.basename(in_path)
            code, meta, out, err = _run_in_isolate(
                box_id,
                run_cmd=run_cmd,
                time_limit=time_limit,
                mem_limit_mb=mem_mb,
                stdin_file=stdin_name,
                stdout_file=f"{name}.stdout",
                stderr_file=f"{name}.stderr",
            )

            # 读取期望输出
            with open(out_path, "r", encoding="utf-8", errors="ignore") as fexp:
                expected = fexp.read()

            # 解析 meta 里的时间/内存（不同 isolate 版本格式略有不同，这里做个弱解析）
            time_used = None
            try:
                meta_lines = {kv.split(":", 1)[0].strip(): kv.split(":", 1)[1].strip()
                              for kv in meta.splitlines() if ":" in kv}
                time_used = float(meta_lines.get("time", "0"))
                status_meta = meta_lines.get("status", "")
            except Exception:
                status_meta = ""

            if status_meta in ("TO", "TL"):  # 超时
                case_status = "time_limit_exceeded"
            elif status_meta in ("RE", "SG"):  # 运行时错误/信号
                case_status = "runtime_error"
            elif code != 0:
                case_status = "runtime_error"
            else:
                # 比对输出
                ok = _normalize(out) == _normalize(expected)
                case_status = "accepted" if ok else "wrong_answer"

            if case_status == "accepted":
                passed += 1

            results.append({
                "name": name,
                "status": case_status,
                "time": time_used,
                "message": err.strip() if err else ""
            })

        overall = "accepted" if passed == len(results) else "rejected"
        score = round(100.0 * passed / max(1, len(results)), 2)

    # 清理 box
    _cleanup_box(box_id)

    return {
        "status": overall,
        "score": score,
        "cases": results,
        "finished_at": datetime.utcnow().isoformat()
    }
