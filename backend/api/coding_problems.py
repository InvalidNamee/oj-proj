from flask import Blueprint, request, jsonify
from exts import db
from models import CodingProblemModel, ProblemSetModel
from decorators import role_required, ROLE_TEACHER
from modules.coding_problem_processing import process_test_cases, remove_test_cases
import json

bp = Blueprint('coding_problems', __name__, url_prefix='/api/coding_problems')

@bp.post('/')
@role_required(ROLE_TEACHER)
def create_coding_problem():
    """
    新建题目
    """
    data = json.loads(request.form['meta'])
    test_cases_zip = request.files.get('test_cases.zip')

    problem = CodingProblemModel(
        title=data.get('title'),
        description=data.get('description'),
        limitations=data.get('limitations'),
    )
    db.session.add(problem)
    db.session.flush()  # 不 commit，先把 pid 刷出来

    problem.test_cases = process_test_cases(problem.id, test_cases_zip)

    db.session.commit()

    return jsonify({'success': 'Problem created successfully', 'id': problem.id}), 201


@bp.delete('/')
@role_required(ROLE_TEACHER)
def delete_coding_problems():
    """
    批量删除 CodingProblem
    """
    data = request.get_json()
    pids = data.get('pids')
    if not pids or not isinstance(pids, list):
        return jsonify({'error': '必须提供 ids 列表'}), 400

    success = True
    results = []

    for pid in pids:
        problem = CodingProblemModel.query.get(pid)
        if not problem:
            results.append({'id': pid, 'status': 'success', 'error': 'Problem not found'})
            success = False
            continue
        remove_test_cases(problem.id, problem.test_cases)
        results.append({'id': pid, 'status': 'success'})
        db.session.delete(problem)

    db.session.commit()
    if success:
        return jsonify({'success': True, 'results': results}), 200
    else:
        return jsonify({'success': False, 'results': results}), 207


@bp.put('/<int:pid>')
@role_required(ROLE_TEACHER)
def update_coding_problem(pid):
    """
    修改题目
    """
    data = json.loads(request.form['meta'])
    test_case_zip = request.files.get('test_cases.zip') or None

    problem = CodingProblemModel.query.get(pid)
    if problem is None:
        return jsonify({'error': 'Problem not found'}), 404

    problem.title = data.get('title')
    problem.description = data.get('description')
    problem.limitations = data.get('limitations')
    problem.test_cases = process_test_cases(pid, test_case_zip)

    db.session.commit()
    return jsonify({'success': 'Problem updated successfully'}), 200


@bp.get('/<int:pid>')
@role_required()
def get_coding_problem(pid):
    """
    查询题目信息。
    """
    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    return jsonify({
        'id': problem.id,
        'title': problem.title,
        'description': problem.description,
        'limitations': problem.limitations,
        'test_cases': problem.test_cases,
        'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
    }), 200

@bp.get('/')
@role_required()
def get_coding_problems():
    """
    列表所有 Coding Problem，可根据题单筛选
    Query 参数：
        problem_set_id: 可选，题单 ID
    """
    problem_set_id = request.args.get('problem_set_id', type=int)

    if problem_set_id:
        problem_set = ProblemSetModel.query.get(problem_set_id)
        if not problem_set:
            return jsonify({'error': 'ProblemSet not found'}), 404
        coding_problems = problem_set.coding_problems
    else:
        coding_problems = CodingProblemModel.query.all()

    problems_list = []
    for problem in coding_problems:
        problems_list.append({
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            'num_test_cases': problem.test_cases['num_cases'] if problem.test_cases else 0
        })

    return jsonify({'coding_problems': problems_list}), 200


@bp.patch('/<int:pid>/test_cases/delete')
@role_required(ROLE_TEACHER)
def delete_test_cases(pid):
    """
    批量删除题目的测试用例
    请求体 JSON: {"cases": [{"in": "...", "out": "...", "name": "..."}]}
    """
    data = request.get_json()
    cases = data.get('cases', [])

    if not pid:
        return jsonify({'error': 'pid is required'}), 400

    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    remove_test_cases(pid, {'cases': cases})

    # 传入空文件重新统计
    problem.test_cases = process_test_cases(pid, None)

    db.session.commit()
    return jsonify({'success': True, 'remaining': problem.test_cases}), 200


@bp.patch('/<int:pid>/test_cases/add')
@role_required(ROLE_TEACHER)
def add_test_cases(pid):
    """
    批量添加题目的测试用例
    """
    test_cases_zip = request.files.get('test_cases.zip')

    if not pid:
        return jsonify({'error': 'pid is required'}), 400

    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    problem.test_cases = process_test_cases(problem.id, test_cases_zip)

    db.session.commit()
    return jsonify({'success': True, 'test_cases': problem.test_cases}), 200
