from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from exts import db
from models import CodingProblemModel, ProblemSetModel, CourseModel, UserModel
from decorators import role_required, ROLE_TEACHER
from modules.coding_problem_processing import process_test_cases, remove_test_cases
from modules.verify import is_admin
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

    course_id = int(data.get('course_id'))
    if not course_id:
        return jsonify({'error': 'course_id is required'}), 400

    user = UserModel.query.get(get_jwt_identity())
    course = CourseModel.query.get(course_id)
    if not course:
        return jsonify({'error': f'Course {course_id} not found'}), 404
    if not is_admin() and course_id not in [c.id for c in user.courses]:
        return jsonify({'error': f'Course {course_id}: Permission denied'}), 403

    problem = CodingProblemModel(
        title=data.get('title'),
        description=data.get('description'),
        limitations=data.get('limitations'),
    )
    problem.course = course
    db.session.add(problem)
    db.session.flush()

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
        return jsonify({'error': 'pids are needed'}), 400

    user = UserModel.query.get(get_jwt_identity())
    success = True
    results = []

    for pid in pids:
        problem = CodingProblemModel.query.get(pid)
        if not problem:
            results.append({'id': pid, 'status': 'fail', 'error': 'Problem not found'})
            success = False
            continue

        if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
            results.append({'id': pid, 'status': 'fail', 'error': 'Permission denied'})
            success = False
            continue

        remove_test_cases(problem.id, problem.test_cases)
        results.append({'id': pid, 'status': 'success'})
        db.session.delete(problem)

    db.session.commit()
    return jsonify({'success': success, 'results': results}), 200 if success else 207


@bp.put('/<int:pid>')
@role_required(ROLE_TEACHER)
def update_coding_problem(pid):
    """
    修改题目
    """
    data = json.loads(request.form['meta'])
    test_case_zip = request.files.get('test_cases.zip') or None

    user = UserModel.query.get(get_jwt_identity())
    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

    problem.title = data.get('title')
    problem.description = data.get('description')
    problem.limitations = data.get('limitations')
    course_id = data.get('course_id')

    if not course_id:
        return jsonify({'error': 'course_id is required'}), 400

    new_course = CourseModel.query.get(course_id)
    if not new_course:
        return jsonify({'error': 'Course not found'}), 404

    if not is_admin() and new_course.id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

    problem.test_cases = process_test_cases(pid, test_case_zip)

    db.session.commit()
    return jsonify({'success': True}), 200


@bp.get('/<int:pid>')
@role_required()
def get_coding_problem(pid):
    """
    查询题目信息
    """
    user = UserModel.query.get(get_jwt_identity())
    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

    return jsonify({
        'id': problem.id,
        'title': problem.title,
        'description': problem.description,
        'limitations': problem.limitations,
        'test_cases': problem.test_cases,
        'course_id': problem.course_id,
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
    problem_set_id = request.args.get('psid', type=int)
    user = UserModel.query.get(get_jwt_identity())

    if problem_set_id:
        problem_set = ProblemSetModel.query.get(problem_set_id)
        if not problem_set:
            return jsonify({'error': 'ProblemSet not found'}), 404
        coding_problems = problem_set.coding_problems
    else:
        if is_admin():
            coding_problems = CodingProblemModel.query.all()
        else:
            course_ids = [c.id for c in user.courses]
            coding_problems = CodingProblemModel.query.filter(
                CodingProblemModel.course_id.in_(course_ids)
            ).all()

    problems_list = []
    for problem in coding_problems:
        problems_list.append({
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'course_id': problem.course_id,
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

    user = UserModel.query.get(get_jwt_identity())
    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # 权限检查
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

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

    user = UserModel.query.get(get_jwt_identity())
    problem = CodingProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # 权限检查
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

    problem.test_cases = process_test_cases(problem.id, test_cases_zip)
    db.session.commit()
    return jsonify({'success': True, 'test_cases': problem.test_cases}), 200
