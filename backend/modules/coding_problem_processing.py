import os
import io
import zipfile
import shutil

def process_test_cases(pid: str, uploaded_file):
    """
    pid: 测试数据标识
    uploaded_file: Flask request.files['test_cases.zip'] 对象
    """
    project_root = os.getcwd()
    base_dir = os.path.join(project_root, 'data', str(pid))
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

            # 相对项目目录的路径
            rel_in = os.path.relpath(new_in, project_root)
            rel_out = os.path.relpath(new_out, project_root)

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

    :param pid: 项目/题目 id，对应 data 目录下的子目录
    :param test_cases_dict: 测试用例字典，例如：
        {
            "cases": [
                {"in": "data/3/2.in", "out": "data/3/2.out", "name": "2"},
                ...
            ],
            "num_cases": 7
        }
    """
    cases = test_cases_dict.get('cases', [])
    base_dir = os.path.join('data', str(pid))
    deleted_dirs = set()

    for case in cases:
        for key in ['in', 'out']:
            fpath = case.get(key)
            if fpath and os.path.isfile(fpath):
                os.remove(fpath)
                deleted_dirs.add(os.path.dirname(fpath))

    # 删除空目录
    if os.path.isdir(base_dir) and not os.listdir(base_dir):
        os.rmdir(base_dir)
