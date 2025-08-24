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
        "-E", "PATH=/usr/bin:/bin",
        "-o", stdout_file,
        "-r", stderr_file,
        "-k", "65536",
        "--"
    ] + run_cmd

    # stdin/stdout/stderr 使用沙箱路径
    if datadir:
        args.insert(3, f"--dir=/data={datadir}",)
    if stdin_file:
        args.insert(3, f"--stdin=/data/{stdin_file}")

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

def judge_submission(
    box_id: int,
    problem_id: int,
    language: str,
    source_code: str,
    limitations: dict
):
    time_limit = float(limitations.get("maxTime", DEFAULT_TIME_LIMIT))
    mem_mb = int(limitations.get("maxMemory", DEFAULT_MEM_LIMIT_MB))

    tests, datadir = _load_testcases(problem_id)
    if not tests:
        return {"status": "IE", "score": 0, "cases": [], "extra": "No testcases"}

    box_dir = f"/var/lib/isolate/{box_id}/box"  # box 的根目录

    _cleanup_box(box_id)  # 清理 box，保证干净
    _ensure_box(box_id)

    # 写入源文件到 box
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
            ["/usr/bin/g++", "-o2", "-std=c++17", "-o", "main", "main.cpp"],
            workdir=box_dir,
            time_limit=10.0,
            mem_limit_mb=1024
        )
        if code != 0:
            _cleanup_box(box_id)
            return {"status": "CE", "score": 0, "cases": [], "message": err or out}
        run_cmd = ["./main"]
    else:
        _cleanup_box(box_id)
        return {"status": "IE", "score": 0, "cases": [], "message": f"Unsupported language: {language}"}

    results = []
    passed = 0
    max_time = 0.0
    max_memory = 0.0

    for name, in_file, out_path in tests:
        code, meta, out, err = _run_in_isolate(
            box_id,
            run_cmd=run_cmd,
            workdir=box_dir,
            datadir=datadir,
            time_limit=time_limit,
            mem_limit_mb=mem_mb,
            stdin_file=in_file,  # 相对路径
            stdout_file=f"{name}.stdout",
            stderr_file=f"{name}.stderr",
        )

        with open(out_path, "r", encoding="utf-8", errors="ignore") as fexp:
            expected = fexp.read()

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
        
        results.append({
            "name": name,
            "status": case_status,
            "time": time_used,
            "memory": peek_memory,
            "message": err.strip() if err else ""
        })

    status_list = [result.get("status") for result in results]
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
