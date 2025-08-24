from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from exts import db
from models import CodingProblemModel, ProblemSetModel, CourseModel, UserModel, SubmissionModel
from decorators import role_required, ROLE_TEACHER
from modules.coding_problem_processing import process_test_cases, remove_test_cases
from modules.verify import is_admin, is_related
import json

bp = Blueprint('coding_problems', __name__, url_prefix='/api/coding_problems')


@bp.post('/')
@role_required(ROLE_TEACHER)
def create_coding_problem():
    """
    新建题目，只接受 JSON
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    course_id = int(data.get('course_id', 0))
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

    problem.test_cases = {
        "cases": [], "num_cases": 0
    }
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
    
    submission = SubmissionModel.query.filter_by(user_id=user.id, problem_id=pid).order_by(SubmissionModel.time_stamp.desc()).first()
    user_answer = submission.user_answer if submission else ''
    language = submission.language if submission else ''
        

    return jsonify({
        'id': problem.id,
        'title': problem.title,
        'description': problem.description,
        'limitations': problem.limitations,
        'test_cases': problem.test_cases,
        'course_id': problem.course_id,
        'user_answer': user_answer,
        'language': language,
        'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
    }), 200


@bp.get('/')
@role_required(ROLE_TEACHER)
def get_coding_problems():
    """
    列表所有 Coding Problem，可根据题单或课程筛选
    Query 参数：
        problem_set_id: 可选，题单 ID
        course_id: 可选，课程 ID
        page: 可选，页码（默认 1）
        per_page: 可选，每页数量（默认 10）
    """
    problem_set_id = request.args.get('problem_set_id', type=int)
    course_id = request.args.get('course_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    user = UserModel.query.get(get_jwt_identity())

    query = CodingProblemModel.query

    if problem_set_id:
        problem_set = ProblemSetModel.query.get_or_404(problem_set_id)
        query = query.filter(CodingProblemModel.problem_sets.contains(problem_set))
    elif course_id:
        if not is_admin() and not is_related(user, course_id):
            return jsonify({'error': 'Permission denied'}), 403
        query = query.filter_by(course_id=course_id)
    elif not is_admin():
        return jsonify({'error': 'Permission denied'}), 403

    pagination = query.order_by(CodingProblemModel.time_stamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    problems_list = []
    for problem in pagination.items:
        problems_list.append({
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'course': {
                'id': problem.course.id,
                'name': problem.course.course_name,
            },
            'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            'num_test_cases': problem.test_cases['num_cases'] if problem.test_cases else 0
        })

    return jsonify({
        'coding_problems': problems_list,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    }), 200

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
