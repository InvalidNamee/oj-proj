import os
import io
import zipfile
import shutil

import os

def process_json_data(pid: str, test_cases: list):
    """
    pid: 测试数据标识
    test_cases: [{id, input, output}, ...]
    将每个测试用例写到 data/{pid}/{id}.in 和 {id}.out
    返回 JSON 信息
    """
    parent_root = os.path.dirname(os.getcwd())
    base_dir = os.path.join(parent_root, "data", str(pid))
    os.makedirs(base_dir, exist_ok=True)

    cases_info = []

    for tc in test_cases:
        tc_id = str(tc["id"])
        input_path = os.path.join(base_dir, f"{tc_id}.in")
        output_path = os.path.join(base_dir, f"{tc_id}.out")

        # 写入 input
        with open(input_path, "w", encoding="utf-8") as f_in:
            f_in.write(tc.get("input", ""))

        # 写入 output
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(tc.get("output", ""))

        cases_info.append({
            "id": tc_id,
            "in": os.path.relpath(input_path, parent_root),
            "out": os.path.relpath(output_path, parent_root)
        })

    return {
        "num_cases": len(cases_info),
        "cases": cases_info
    }


def process_test_cases(pid: str, uploaded_file):
    """
    pid: 测试数据标识
    uploaded_file: Flask request.files['test_cases.zip'] 对象
    """
    project_root = os.getcwd()
    parent_root = os.path.dirname(project_root)   # 上一级目录
    base_dir = os.path.join(parent_root, 'data', str(pid))
    os.makedirs(base_dir, exist_ok=True)

    # 1. 从内存读取 ZIP 并解压
    if uploaded_file:
        file_bytes = uploaded_file.read()
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zip_ref:
            zip_ref.extractall(base_dir)

    # 2. 收集所有文件（递归一层）
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        if root != base_dir:
            dirs[:] = []  # 不进入孙目录
        for f in files:
            all_files.append(os.path.join(root, f))

    test_cases = []
    valid_files = set()

    # 3. 找到匹配的 .in/.out 文件
    for fpath in all_files:
        fname = os.path.basename(fpath)
        if fname.startswith('._') or not fname.endswith('.in'):
            continue  # 忽略 macOS 隐藏文件和非 .in 文件

        name = os.path.splitext(fname)[0]
        out_name = name + '.out'

        out_path = next((p for p in all_files if os.path.basename(p) == out_name), None)
        if out_path:
            # 移动到 base_dir 根目录
            new_in = os.path.join(base_dir, fname)
            new_out = os.path.join(base_dir, os.path.basename(out_path))
            shutil.move(fpath, new_in)
            shutil.move(out_path, new_out)

            # 相对父目录的路径（因为已经换了 base_dir）
            rel_in = os.path.relpath(new_in, parent_root)
            rel_out = os.path.relpath(new_out, parent_root)

            test_cases.append({
                'name': name,
                'in': rel_in,
                'out': rel_out
            })
            valid_files.update([new_in, new_out])

    # 4. 删除无关文件和空目录
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for f in files:
            fpath = os.path.join(root, f)
            if fpath not in valid_files:
                os.remove(fpath)
        for d in dirs:
            dpath = os.path.join(root, d)
            if not os.listdir(dpath):
                os.rmdir(dpath)

    # 5. 返回 JSON
    return {
        'num_cases': len(test_cases),
        'cases': test_cases
    }


def remove_test_cases(pid: str, test_cases_dict: dict):
    """
    删除指定 pid 的测试用例文件。
    """
    parent_root = os.path.dirname(os.getcwd())
    base_dir = os.path.join(parent_root, 'data', str(pid))
    cases = test_cases_dict.get('cases', [])

    for case in cases:
        for key in ['in', 'out']:
            fpath = case.get(key)
            if fpath:
                abs_path = os.path.join(parent_root, fpath)
                if os.path.isfile(abs_path):
                    os.remove(abs_path)

    # 删除空目录
    if os.path.isdir(base_dir) and not os.listdir(base_dir):
        os.rmdir(base_dir)


def pack_test_cases(pid: str):
    """
    打包指定 pid 的测试用例目录为 zip 并返回文件对象
    """
    parent_root = os.path.dirname(os.getcwd())
    base_dir = os.path.join(parent_root, 'data', str(pid))

    if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
        raise FileNotFoundError("测试用例目录不存在")

    # 收集所有文件（只看 base_dir 里的一层）
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        if root != base_dir:
            dirs[:] = []  # 不进入子目录
        for f in files:
            all_files.append(os.path.join(root, f))

    if not all_files:
        raise FileNotFoundError("测试用例目录为空")

    # 写 zip 到内存
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in all_files:
            # 在 zip 内部的路径（保持在 pid/ 下）
            arcname = os.path.relpath(file_path, parent_root)
            zf.write(file_path, arcname)
    memory_file.seek(0)

    return memory_file