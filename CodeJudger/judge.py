import os
import json
import tempfile
import subprocess
from glob import glob
from datetime import datetime
from typing import List, Tuple
from config import DATA_DIR, DEFAULT_TIME_LIMIT, DEFAULT_MEM_LIMIT_MB, DEFAULT_OUTPUT_LIMIT_KB, MAX_DIFF_LEN

class JudgeError(Exception):
    pass

def _run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def _ensure_box(box_id: int) -> None:
    _run_cmd(["isolate", f"--box-id={box_id}", "--init", "--cg"])

def _cleanup_box(box_id: int) -> None:
    _run_cmd(["isolate", f"--box-id={box_id}", "--cleanup", "--cg"])

def _run_in_isolate(
    box_id: int,
    run_cmd: List[str],
    workdir: str,
    time_limit: float,
    mem_limit_mb: int,
    datadir: str = '',
    stdin_file: str = '',
    stdout_file: str = "stdout.txt",
    stderr_file: str = "stderr.txt",
    fsize_kb: int = DEFAULT_OUTPUT_LIMIT_KB
) -> Tuple[int, str, str, str] | None:

    with tempfile.NamedTemporaryFile(prefix="iso_meta_", delete=False) as meta_tmp:
        meta_path = meta_tmp.name

    args = [
        "isolate",
        f"--box-id={box_id}",
        "--run",
        "--cg",
        f"--time={time_limit}",
        f"--mem={mem_limit_mb * 1024}",
        f"--fsize={fsize_kb}",
        "--meta", meta_path,
        "--cg-mem", str(mem_limit_mb * 1024),
        "-p",
        "-E", "PATH=/usr/bin:/usr/bin",
        "-o", stdout_file,
        "-r", stderr_file,
        "-k", "65536",
        "--"
    ] + run_cmd

    # stdin/stdout/stderr 使用沙箱路径
    if datadir:
        args.insert(3, f"--dir=/data={datadir}",)
        args.insert(3, f"--stdin=/data/{stdin_file}")
    elif stdin_file:
        args.insert(3, f"--stdin=data/{stdin_file}")

    proc = _run_cmd(args)

    # 宿主机上的对应文件路径
    stdout_path = os.path.join(workdir, stdout_file)
    stderr_path = os.path.join(workdir, stderr_file)

    out, err = "", ""
    if os.path.exists(stdout_path):
        with open(stdout_path, "r", encoding="utf-8", errors="ignore") as f:
            out = f.read()
    if os.path.exists(stderr_path):
        with open(stderr_path, "r", encoding="utf-8", errors="ignore") as f:
            err = f.read()

    # 读取 meta
    meta = ""
    try:
        with open(meta_path, "r") as f:
            meta = f.read()
    finally:
        os.unlink(meta_path)

    return proc.returncode, meta, out, err


def _load_testcases(problem_id: int):
    base = os.path.join(DATA_DIR, str(problem_id))
    ins = sorted(glob(os.path.join(base, "*.in")))
    dataset = []
    for in_path in ins:
        name = os.path.splitext(os.path.basename(in_path))[0]
        out_path = os.path.join(base, f"{name}.out")
        if os.path.exists(out_path):
            # 保存相对路径
            dataset.append((name, os.path.basename(in_path), out_path))
    return dataset, base

def _normalize(s: str) -> str:
    return "\n".join([line.rstrip() for line in s.rstrip().splitlines()])

def _get_diff(expected: str, actual: str) -> str:
    """生成简易 diff（只取前 MAX_DIFF_LEN 字符）"""
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    diffs = []
    for i, (e, a) in enumerate(zip(expected_lines, actual_lines)):
        if e != a:
            diffs.append(f"Line {i+1}:\n  Expected: {e}\n  Actual:   {a}")
    # 多余行
    for i in range(len(actual_lines), len(expected_lines)):
        diffs.append(f"Line {i+1}:\n  Expected: {expected_lines[i]}\n  Actual:   <no line>")
    for i in range(len(expected_lines), len(actual_lines)):
        diffs.append(f"Line {i+1}:\n  Expected: <no line>\n  Actual:   {actual_lines[i]}")
    diff_text = "\n".join(diffs)
    if len(diff_text) > MAX_DIFF_LEN:
        diff_text = diff_text[:MAX_DIFF_LEN] + "\n...[truncated]..."
    return diff_text


def judge_submission(
    box_id: int,
    problem_id: int,
    language: str,
    source_code: str,
    limitations: dict,
    test_cases: list | None = None,
):
    time_limit = float(limitations.get("maxTime", DEFAULT_TIME_LIMIT))
    mem_mb = int(limitations.get("maxMemory", DEFAULT_MEM_LIMIT_MB))

    # 如果没有传入 test_cases，就按原来的读取文件
    if test_cases is None:
        tests, datadir = _load_testcases(problem_id)
        if not tests:
            return {"status": "IE", "score": 0, "cases": [], "extra": "No testcases"}
        use_files = True
    else:
        # 将 test_cases 转成 [(name, input_file, expected_output_file)] 的形式，但这里不读文件
        tests = []
        for i, tc in enumerate(test_cases):
            name = tc.get("id", f"case_{i}")
            tests.append((name, tc.get("input", ""), tc.get("output", "")))
        use_files = False
        datadir = ""  # 不需要绑定目录

    box_dir = f"/var/lib/isolate/{box_id}/box"

    _cleanup_box(box_id)
    _ensure_box(box_id)
    os.makedirs(f"{box_dir}/data", exist_ok=True)

    # 写入源文件
    if language == "python":
        src_path = os.path.join(box_dir, "main.py")
        with open(src_path, "w") as f:
            f.write(source_code)
        run_cmd = ["/usr/bin/python3", "main.py"]
    elif language == "cpp":
        src_path = os.path.join(box_dir, "main.cpp")
        with open(src_path, "w") as f:
            f.write(source_code)
        code, meta, out, err = _run_in_isolate(
            box_id,
            ["/usr/bin/g++", "-O2", "-std=c++17", "-o", "main", "main.cpp"],
            workdir=box_dir,
            time_limit=10.0,
            mem_limit_mb=1024
        )
        if code != 0:
            _cleanup_box(box_id)
            print(code, meta, out, err)
            return {"status": "CE", "score": 0, "cases": [], "message": err or out}
        run_cmd = ["./main"]
    elif language == "java":
        src_path = os.path.join(box_dir, "Main.java")
        with open(src_path, "w") as f:
            f.write(source_code)
        # 编译
        code, meta, out, err = _run_in_isolate(
            box_id,
            ["/usr/bin/javac", "Main.java"],
            workdir=box_dir,
            time_limit=10.0,
            mem_limit_mb=1024
        )
        if code != 0:
            print(code, meta, out, err)
            _cleanup_box(box_id)
            return {"status": "CE", "score": 0, "cases": [], "message": err or out}

        # 运行
        run_cmd = ["/usr/bin/java", "-cp", ".", "Main"]
    else:
        _cleanup_box(box_id)
        return {"status": "IE", "score": 0, "cases": [], "message": f"Unsupported language: {language}"}

    results = []
    passed = 0
    max_time = 0.0
    max_memory = 0.0

    for name, input_data_or_file, expected_output_or_file in tests:
        if use_files:
            # 正常提交模式，绑定文件
            code, meta, out, err = _run_in_isolate(
                box_id,
                run_cmd=run_cmd,
                workdir=box_dir,
                datadir=datadir,
                time_limit=time_limit,
                mem_limit_mb=mem_mb,
                stdin_file=input_data_or_file,
                stdout_file=f"{name}.stdout",
                stderr_file=f"{name}.stderr",
            )
            with open(expected_output_or_file, "r", encoding="utf-8", errors="ignore") as fexp:
                expected = fexp.read()
        else:
            # 自测模式，直接在 box 创建输入文件
            input_path = os.path.join(box_dir, f"data/{name}.in")
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(input_data_or_file)
            expected = expected_output_or_file
            code, meta, out, err = _run_in_isolate(
                box_id,
                run_cmd=run_cmd,
                workdir=box_dir,
                time_limit=time_limit,
                mem_limit_mb=mem_mb,
                stdin_file=f"{name}.in",
                stdout_file=f"{name}.stdout",
                stderr_file=f"{name}.stderr",
            )

        # 解析 meta
        time_used = None
        peek_memory = None
        try:
            meta_lines = {kv.split(":", 1)[0].strip(): kv.split(":", 1)[1].strip()
                          for kv in meta.splitlines() if ":" in kv}
            time_used = float(meta_lines.get("time", "0")) * 1000
            peek_memory = float(meta_lines.get("max-rss", "0"))
            status_meta = meta_lines.get("status", "")
        except Exception:
            status_meta = ""

        # 判定状态
        if status_meta in ("TO", "TL"):
            case_status = "TLE"
        elif status_meta in ("RE", "SG"):
            if meta_lines.get("exitsig") == "25":
                case_status = "OLE"
            elif meta_lines.get("exitsig") == "11":
                case_status = "MLE"
            else:
                case_status = "RE"
        elif code != 0:
            case_status = "RE"
        else:
            ok = _normalize(out) == _normalize(expected)
            case_status = "AC" if ok else "WA"

        if case_status == "AC":
            passed += 1
        max_time = max(max_time, time_used)
        max_memory = max(max_memory, peek_memory)
        diff_text = _get_diff(expected, out) if case_status == "WA" else ""

        results.append({
            "name": name,
            "status": case_status,
            "time": time_used,
            "memory": peek_memory,
            "message": err.strip() if err else "",
            "diff": diff_text
        })

    status_list = [r["status"] for r in results]
    overall = "WA"
    if passed == len(status_list):
        overall = "AC"
    elif "RE" in status_list:
        overall = "RE"
    elif "MLE" in status_list:
        overall = "MLE"
    elif "OLE" in status_list:
        overall = "OLE"
    elif "WA" in status_list:
        overall = "WA"
    elif "TLE" in status_list:
        overall = "TLE"

    score = round(100.0 * passed / max(1, len(results)), 2)
    _cleanup_box(box_id)

    return {
        "status": overall,
        "score": score,
        "max_time": max_time,
        "max_memory": max_memory,
        "cases": results,
        "finished_at": datetime.now().isoformat()
    }
