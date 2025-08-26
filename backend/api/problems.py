from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from exts import db
from models import ProblemModel, ProblemSetModel, CourseModel, UserModel, SubmissionModel
from decorators import role_required, ROLE_TEACHER
from modules.testcases_processing import process_test_cases, remove_test_cases, pack_test_cases
from modules.verify import is_admin, is_related

bp = Blueprint('problems', __name__, url_prefix='/api/problems')

# 传统问题并到这里了
@bp.post('/legacy')
@role_required(ROLE_TEACHER)
def create_legacy():
    """
    新建传统题目
    :return:
    """
    user = UserModel.query.get(get_jwt_identity())
    data = request.get_json()
    title = data.get('title')
    problem_type = data.get('type')
    description = data.get('description')
    test_cases = data.get('test_cases')
    course_id = data.get('course_id')

    course = CourseModel.query.get_or_404(course_id)
    if not is_related(user, course_id):
        return jsonify({'error': 'Permission denied'}), 403

    problem = ProblemModel(
        title=title,
        description=description,
        test_cases=test_cases,
        course=course,
        type=problem_type,
    )
    db.session.add(problem)
    db.session.commit()
    return jsonify({'success': True, 'id': problem.id}), 201

@bp.put('/<int:pid>/legacy')
@role_required(ROLE_TEACHER)
def update_legacy(pid):
    """
    更新传统题目
    """
    user = UserModel.query.get(get_jwt_identity())
    problem = ProblemModel.query.get_or_404(pid)

    # 权限检查：教师必须关联课程，管理员除外
    if not is_related(user, problem.course_id):
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    test_cases = data.get('test_cases')
    course_id = data.get('course_id')

    if course_id:
        course = CourseModel.query.get_or_404(course_id)
        if not is_related(user, course_id):
            return jsonify({'error': 'Permission denied for new course'}), 403
        problem.course = course

    # 更新字段
    if title is not None:
        problem.title = title
    if description is not None:
        problem.description = description
    if test_cases is not None:
        problem.test_cases = test_cases

    db.session.commit()
    return jsonify({'success': True, 'id': problem.id}), 200


# @bp.post('/generate')
# @role_required(ROLE_TEACHER)
# def generate():
#


@bp.post('/')
@role_required(ROLE_TEACHER)
def create_problem():
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
    course = CourseModel.query.get_or_404(course_id)
    if not is_related(user, course_id):
        return jsonify({'error': f'Course {course_id}: Permission denied'}), 403

    problem = ProblemModel(
        title=data.get('title'),
        type='coding',
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
def delete_problems():
    """
    批量删除
    """
    data = request.get_json()
    pids = data.get('pids')
    if not pids or not isinstance(pids, list):
        return jsonify({'error': 'pids are needed'}), 400

    user = UserModel.query.get(get_jwt_identity())
    success = True
    results = []

    for pid in pids:
        problem = ProblemModel.query.get(pid)
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
def update_problem(pid):
    """
    修改题目
    """
    data = request.get_json()
    user = UserModel.query.get(get_jwt_identity())
    problem = ProblemModel.query.get_or_404(pid)
    if not is_related(user, problem.course_id):
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

    db.session.commit()
    return jsonify({'success': True}), 200


@bp.get('/<int:pid>')
@role_required()
def get_problem(pid):
    """
    查询题目信息
    """
    user = UserModel.query.get(get_jwt_identity())
    problem = ProblemModel.query.get_or_404(pid)
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403
    
    submission = SubmissionModel.query.filter_by(user_id=user.id, problem_id=pid).order_by(SubmissionModel.time_stamp.desc()).first()
    user_answer = submission.user_answer if submission else None
    language = submission.language if submission else ''
        

    return jsonify({
        'id': problem.id,
        'title': problem.title,
        'type': problem.type,
        'description': problem.description,
        'limitations': problem.limitations,
        'test_cases': problem.test_cases if problem.type == 'coding' else {'options': problem.test_cases.get('options')},
        'course_id': problem.course_id,
        'user_answer': user_answer,
        'language': language,
        'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
    }), 200


@bp.get('/')
@role_required(ROLE_TEACHER)
def get_problems():
    """
    列表所有 Coding Problem，可根据题单、课程或标题关键词筛选
    Query 参数：
        problem_set_id: 可选，题单 ID
        course_id: 可选，课程 ID
        keyword: 可选，标题关键词
        page: 可选，页码（默认 1）
        per_page: 可选，每页数量（默认 10）
    """
    problem_set_id = request.args.get('problem_set_id', type=int)
    course_id = request.args.get('course_id', type=int)
    keyword = request.args.get('keyword', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    user = UserModel.query.get(get_jwt_identity())

    query = ProblemModel.query

    if problem_set_id:
        problem_set = ProblemSetModel.query.get_or_404(problem_set_id)
        query = query.filter(ProblemModel.problem_sets.contains(problem_set))
    elif course_id:
        if not is_admin() and not is_related(user, course_id):
            return jsonify({'error': 'Permission denied'}), 403
        query = query.filter_by(course_id=course_id)
    elif not is_admin():
        return jsonify({'error': 'Permission denied'}), 403

    # 标题关键词过滤
    if keyword:
        query = query.filter(ProblemModel.title.ilike(f'%{keyword}%'))

    pagination = query.order_by(ProblemModel.time_stamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    problems_list = []
    for problem in pagination.items:
        num_cases = problem.test_cases.get('num_cases')
        problems_list.append({
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'type': problem.type,
            'course': {
                'id': problem.course.id,
                'name': problem.course.course_name,
            },
            'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            'num_test_cases': num_cases if num_cases else '-',
        })

    return jsonify({
        'problems': problems_list,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    }), 200


@bp.get('/<int:pid>/test_cases/download')
@role_required(ROLE_TEACHER)
def download_test_cases(pid):
    """
    下载测试用例
    """
    try:
        memory_file = pack_test_cases(pid)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    return send_file(
        memory_file,
        as_attachment=True,
        download_name=f"test_cases_{pid}.zip",
        mimetype="application/zip"
    )


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
    problem = ProblemModel.query.get_or_404(pid)

    if problem.type != 'coding':
        return jsonify({'error': 'Operation not permitted'}), 400

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
    problem = ProblemModel.query.get_or_404(pid)

    if problem.type != 'coding':
        return jsonify({'error': 'Operation not permitted'}), 400
    # 权限检查
    if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
        return jsonify({'error': 'Permission denied'}), 403

    problem.test_cases = process_test_cases(problem.id, test_cases_zip)
    db.session.commit()
    return jsonify({'success': True, 'test_cases': problem.test_cases}), 200
