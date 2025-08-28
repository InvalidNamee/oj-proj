# docker_judge.py
import os
import shlex
import json
import tempfile
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from glob import glob
from config import *

class JudgeError(Exception):
    pass

def _safe_write(path: str, content: str, encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)

def _truncate_text(text: str, max_kb: int):
    max_bytes = max_kb * 1024
    enc = text.encode('utf-8', errors='ignore')
    if len(enc) <= max_bytes:
        return text
    return enc[:max_bytes].decode('utf-8', errors='ignore')

def _get_diff(expected: str, actual: str) -> str:
    expected_lines = expected.rstrip().splitlines()
    actual_lines = actual.rstrip().splitlines()
    diffs = []
    for i in range(max(len(expected_lines), len(actual_lines))):
        e = expected_lines[i] if i < len(expected_lines) else None
        a = actual_lines[i] if i < len(actual_lines) else None
        if e != a:
            diffs.append(f"Line {i+1}:\n  Expected: {e if e is not None else '<no line>'}\n  Actual:   {a if a is not None else '<no line>'}")
        if len("\n".join(diffs)) > MAX_DIFF_LEN:
            diffs = ["[diff truncated]"]
            break
    return "\n".join(diffs)

def _normalize(s: str) -> str:
    return "\n".join([line.rstrip() for line in s.rstrip().splitlines()])

def _run_docker_shell(
    image: str,
    shell_cmd: str,
    workdir: str,
    mem_limit_mb: int,
) -> Tuple[int, str, str]:
    os.makedirs(workdir, exist_ok=True)
    mount = f"{os.path.abspath(workdir)}:/app:rw"

    docker_base = [
        "docker", "run", "--rm",
        "--network=none",
        f"--memory={mem_limit_mb}m",
        f"--memory-swap={mem_limit_mb}m",
        "--pids-limit=128",
        "-v", mount,
        "-w", "/app",
        image,
        "bash", "-lc"
    ]
    quoted = shlex.quote(shell_cmd)
    full_cmd = docker_base + [quoted]
    print(' '.join(full_cmd))

    proc = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout = proc.stdout
    stderr = proc.stderr
    _safe_write(os.path.join(workdir, "docker_stdout.txt"), _truncate_text(stdout, DEFAULT_OUTPUT_LIMIT_KB))
    _safe_write(os.path.join(workdir, "docker_stderr.txt"), _truncate_text(stderr, DEFAULT_OUTPUT_LIMIT_KB))
    return proc.returncode, stdout, stderr

def _collect_test_files(problem_id: int) -> Tuple[List[Tuple[str,str,str]], str]:
    """
    返回 ( [(name, in_filename, out_filepath), ...], base_dir )
    in_filename 仅是文件名 (basename)，out_filepath 是宿主机绝对路径
    """
    base = os.path.join(DATA_DIR, str(problem_id))
    if not os.path.isdir(base):
        return [], base
    ins = sorted(glob(os.path.join(base, "*.in")))
    dataset = []
    for in_path in ins:
        name = os.path.splitext(os.path.basename(in_path))[0]
        out_path = os.path.join(base, f"{name}.out")
        if os.path.exists(out_path):
            dataset.append((name, os.path.basename(in_path), out_path))
    return dataset, base

def judge_submission_docker(
    image: str,
    problem_id: int,
    language: str,
    source_code: str,
    limitations: Dict,
    test_cases: Optional[List[Dict]] = None,
    keep_workdir: bool = False
):
    """
    - image: docker 镜像名（需包含 python3, g++, javac/java, /usr/bin/time, timeout）
    - 如果 test_cases is None -> 使用文件模式，从 DATA_DIR/<problem_id> 读取 *.in/*.out 并只读挂载到容器 /app/data
    - 如果 test_cases 列表 -> 内存模式（自测），在工作目录创建输入文件再运行
    - keep_workdir=True 会保留宿主机工作目录（便于调试）
    """
    time_limit = float(limitations.get("maxTime", DEFAULT_TIME_LIMIT))
    mem_mb = int(limitations.get("maxMemory", DEFAULT_MEM_LIMIT_MB))
    fsize_kb = int(limitations.get("maxOutput", DEFAULT_OUTPUT_LIMIT_KB))

    if keep_workdir:
        workdir = os.path.abspath(f"./docker_judge_keep_{int(datetime.now().timestamp())}")
        os.makedirs(workdir, exist_ok=True)
        temp_created = False
    else:
        workdir = tempfile.mkdtemp(prefix="docker_judge_")
        temp_created = True

    try:
        # ---- 1. 选择测试集来源 ----
        use_file_mode = test_cases is None
        print(use_file_mode)
        file_tests = []
        datadir = ""
        if use_file_mode:
            file_tests, datadir = _collect_test_files(problem_id)
            if not file_tests:
                return {"status":"IE", "score":0, "cases":[], "message":"No test files found"}
            # file_tests: list of (name, in_basename, out_abs_path)
        else:
            # prepare test_cases: ensure id, input, output
            # create (name, input, output) list for uniform processing
            file_tests = []
            for i, tc in enumerate(test_cases):
                name = str(tc.get("id", f"case_{i}"))
                file_tests.append((name, None, None))
                # we will write input files in workdir below for memory mode

        # ---- 2. 写源文件并编译（如果需要） ----
        if language == "python":
            src_name = "main.py"
            _safe_write(os.path.join(workdir, src_name), source_code)
            run_cmd = f"python3 {shlex.quote(src_name)}"
        elif language == "cpp":
            src_name = "main.cpp"
            _safe_write(os.path.join(workdir, src_name), source_code)
            compile_cmd = "g++ -O2 -std=c++17 main.cpp -o main 2> compile_stderr.txt || echo __COMPILE_FAILED__"
            code, out, err = _run_docker_shell(image, compile_cmd, workdir, mem_mb)
            comp_stderr = ""
            if os.path.exists(os.path.join(workdir,"compile_stderr.txt")):
                comp_stderr = open(os.path.join(workdir,"compile_stderr.txt"), "r", encoding="utf-8", errors="ignore").read()
            if not os.path.exists(os.path.join(workdir, "main")):
                return {"status":"CE", "score":0, "cases":[], "message": comp_stderr or out or err}
            run_cmd = "./main"
        elif language == "java":
            src_name = "Main.java"
            _safe_write(os.path.join(workdir, src_name), source_code)
            compile_cmd = "javac Main.java 2> compile_stderr.txt || echo __COMPILE_FAILED__"
            code, out, err = _run_docker_shell(image, compile_cmd, workdir, mem_mb)
            comp_stderr = ""
            if os.path.exists(os.path.join(workdir,"compile_stderr.txt")):
                comp_stderr = open(os.path.join(workdir,"compile_stderr.txt"), "r", encoding="utf-8", errors="ignore").read()
            if not os.path.exists(os.path.join(workdir, "Main.class")):
                return {"status":"CE", "score":0, "cases":[], "message": comp_stderr or out or err}
            run_cmd = "java -cp . Main"
        else:
            return {"status":"IE", "score":0, "cases":[], "message":f"Unsupported language: {language}"}

        # ---- 3. 如果是内存模式，事先在 workdir/data 写入输入文件；如果是文件模式，将 datadir 只读挂载 ----
        if use_file_mode:
            # datadir must exist
            if not os.path.isdir(datadir):
                return {"status":"IE","score":0,"cases":[],"message":"Data dir not found"}
            # we'll mount datadir -> /app/data:ro in docker run invocation below
            mount_data_flag = True
        else:
            # create data dir under workdir and write inputs
            data_dir_host = os.path.join(workdir, "data")
            os.makedirs(data_dir_host, exist_ok=True)
            for (name, _, _) in file_tests:
                # find original tc object by id from provided list
                # build mapping from name->tc
                pass
            # Actually write inputs from provided test_cases
            for i, tc in enumerate(test_cases):
                name = str(tc.get("id", i+1))
                in_host = os.path.join(workdir, f"{name}.in")
                _safe_write(in_host, tc.get("input", ""))
            mount_data_flag = False
            datadir = ""  # not used in file mode

        # ---- 4. 逐个运行测试 ----
        results = []
        passed = 0
        max_time_ms = 0.0
        max_memory_kb = 0.0

        # Helper to run one test; handles mounting datadir read-only if needed
        def _run_one_test(name: str, in_basename: Optional[str], expected_host_out_path: Optional[str], input_text: Optional[str]):
            """
            in_basename: when file mode -> basename of the .in file located in datadir
            expected_host_out_path: absolute path to expected .out on host (only file mode)
            input_text: when memory mode -> content string
            """
            # ensure per-test working subdir (container will write stdout.txt etc to /app)
            # We'll use the top-level workdir for outputs (stdout.txt, stderr.txt, meta.txt)
            # Build shell command: timeout ... "/usr/bin/time -f 'time:%e\nmax-rss:%M' -o meta.txt -- {run_cmd} < <input> > stdout.txt 2> stderr.txt ; echo $? > exitcode.txt"
            # Input file path inside container:
            if use_file_mode:
                container_input = f"/app/data/{in_basename}"
            else:
                # input file we created at host: workdir/<name>.in -> mounted to /app/<name>.in
                container_input = f"/app/{name}.in"

            # build the actual shell (we quote carefully)
            # note: run inside bash -lc so quoting is simpler
            shell_cmd = (
                f"timeout -s KILL {time_limit}s bash -lc "
                f"\"/usr/bin/time -f 'time:%e\\nmax-rss:%M' -o meta.txt -- {run_cmd} < {shlex.quote(container_input)} > stdout.txt 2> stderr.txt; echo $? > exitcode.txt\""
            )

            # prepare docker run base and extra mount if needed
            os.makedirs(workdir, exist_ok=True)
            mount = f"{os.path.abspath(workdir)}:/app:rw"
            docker_cmd = [
                "docker", "run", "--rm",
                "--network=none",
                f"--memory={mem_mb}m",
                f"--memory-swap={mem_mb}m",
                "--pids-limit=128",
                "-v", mount,
                "-w", "/app"
            ]
            # if file-mode, add read-only mount for datadir -> /app/data
            if use_file_mode:
                docker_cmd += ["-v", f"{os.path.abspath(datadir)}:/app/data:ro"]
            docker_cmd += [image, "bash", "-lc", shlex.quote(shell_cmd)]

            proc = subprocess.run(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # read produced files on host (workdir)
            stdout_text = ""
            stderr_text = ""
            meta_text = ""
            exit_code_inner = None
            stdout_path = os.path.join(workdir, "stdout.txt")
            stderr_path = os.path.join(workdir, "stderr.txt")
            meta_path = os.path.join(workdir, "meta.txt")
            exitcode_path = os.path.join(workdir, "exitcode.txt")
            if os.path.exists(stdout_path):
                with open(stdout_path, "r", encoding="utf-8", errors="ignore") as f:
                    stdout_text = f.read()
            if os.path.exists(stderr_path):
                with open(stderr_path, "r", encoding="utf-8", errors="ignore") as f:
                    stderr_text = f.read()
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8", errors="ignore") as f:
                    meta_text = f.read()
            if os.path.exists(exitcode_path):
                try:
                    exit_code_inner = int(open(exitcode_path,"r").read().strip())
                except Exception:
                    exit_code_inner = None

            # determine status & parse meta
            time_used_ms = None
            peak_rss_kb = None
            try:
                for line in meta_text.splitlines():
                    if line.startswith("time:"):
                        val = line.split(":",1)[1].strip()
                        time_used_ms = float(val) * 1000.0
                    elif line.startswith("max-rss:"):
                        peak_rss_kb = float(line.split(":",1)[1].strip())
            except Exception:
                pass

            # get expected output
            expected = ""
            if use_file_mode and expected_host_out_path and os.path.exists(expected_host_out_path):
                with open(expected_host_out_path, "r", encoding="utf-8", errors="ignore") as f:
                    expected = f.read()

            # decide case status
            case_status = "AC"
            if exit_code_inner is None:
                # use proc.returncode & stderr hints
                if "Timed out" in proc.stderr or "Killed" in proc.stderr or "timeout" in proc.stderr.lower():
                    case_status = "TLE"
                else:
                    case_status = "RE"
            else:
                if exit_code_inner != 0:
                    if exit_code_inner == 124:
                        case_status = "TLE"
                    elif exit_code_inner == 137:
                        case_status = "MLE"
                    else:
                        case_status = "RE"
                else:
                    # compare output
                    ok = False
                    if use_file_mode:
                        ok = _normalize(stdout_text) == _normalize(expected)
                    else:
                        # memory mode we have expected in the original tc['output']
                        ok = _normalize(stdout_text) == _normalize(input_text_and_expected_mapping.get(name, ""))
                    case_status = "AC" if ok else "WA"

            return {
                "stdout": _truncate_text(stdout_text, fsize_kb),
                "stderr": _truncate_text(stderr_text, fsize_kb),
                "meta": meta_text,
                "exit_code": exit_code_inner,
                "time_ms": time_used_ms,
                "mem_kb": peak_rss_kb,
                "status": case_status,
                "expected": expected
            }

        # For memory-mode expected lookup mapping:
        input_text_and_expected_mapping = {}
        if not use_file_mode:
            for tc in test_cases:
                name = str(tc.get("id", tc.get("name", "")))
                input_text_and_expected_mapping[name] = tc.get("output", "")

        # iterate tests
        for idx, tup in enumerate(file_tests):
            name, in_basename, out_abs = tup
            if use_file_mode:
                res = _run_one_test(name, in_basename, out_abs, None)
            else:
                # memory mode: we wrote workdir/<name>.in earlier
                # ensure the input file exists at workdir/<name>.in
                input_text = test_cases[idx].get("input","")
                in_host = os.path.join(workdir, f"{name}.in")
                _safe_write(in_host, input_text)
                res = _run_one_test(name, None, None, input_text)

            case_status = res["status"]
            if case_status == "AC":
                passed += 1
            if res["time_ms"]:
                max_time_ms = max(max_time_ms, res["time_ms"])
            if res["mem_kb"]:
                max_memory_kb = max(max_memory_kb, res["mem_kb"])
            diff_text = ""
            if case_status == "WA":
                # build diff between expected and stdout
                expected_text = res["expected"] if use_file_mode else input_text_and_expected_mapping.get(name,"")
                diff_text = _get_diff(expected_text, res["stdout"])

            results.append({
                "name": name,
                "status": case_status,
                "time": res["time_ms"],
                "memory": res["mem_kb"],
                "message": res["stderr"] or "",
                "diff": diff_text
            })

            # cleanup per-test outputs if not keep_workdir
            for fname in ("stdout.txt","stderr.txt","meta.txt","exitcode.txt"):
                p = os.path.join(workdir, fname)
                try:
                    if os.path.exists(p) and not keep_workdir:
                        os.remove(p)
                except Exception:
                    pass

        # overall
        overall = "WA"
        if passed == len(results) and len(results) > 0:
            overall = "AC"
        elif any(r["status"]=="RE" for r in results):
            overall = "RE"
        elif any(r["status"]=="MLE" for r in results):
            overall = "MLE"
        elif any(r["status"]=="OLE" for r in results):
            overall = "OLE"
        elif any(r["status"]=="WA" for r in results):
            overall = "WA"
        elif any(r["status"]=="TLE" for r in results):
            overall = "TLE"

        score = round(100.0 * passed / max(1, len(results)), 2)

        ret = {
            "status": overall,
            "score": score,
            "max_time": max_time_ms,
            "max_memory": max_memory_kb,
            "cases": results,
            "finished_at": datetime.now().isoformat()
        }
        if keep_workdir:
            ret["workdir"] = workdir
        return ret

    finally:
        if temp_created and (not keep_workdir):
            try:
                for root, dirs, files in os.walk(workdir, topdown=False):
                    for name in files:
                        os.unlink(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(workdir)
            except Exception:
                pass
