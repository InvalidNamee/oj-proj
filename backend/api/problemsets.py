from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import CourseModel, LegacyProblemModel, CodingProblemModel, ProblemSetModel, SubmissionModel
from decorators import role_required, ROLE_TEACHER

bp = Blueprint('problemsets', __name__, url_prefix='/api/problemsets')

@bp.post('/')
@role_required(ROLE_TEACHER)
def create_problemset():
    """
    新建题单
    """
    data = request.get_json()
    title = data.get('title')
    course_id = data.get('course_id')
    description = data.get('description')
    legacy_problem_ids = data.get('legacy_problem_ids', [])
    coding_problem_ids = data.get('coding_problem_ids', [])

    course = None
    if course_id:
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 400

    problem_set = ProblemSetModel(
        title=title,
        description=description,
        course=course
    )

    # 关联题目
    if legacy_problem_ids:
        problem_set.legacy_problems = LegacyProblemModel.query.filter(
            LegacyProblemModel.id.in_(legacy_problem_ids)
        ).all()

    if coding_problem_ids:
        problem_set.coding_problems = CodingProblemModel.query.filter(
            CodingProblemModel.id.in_(coding_problem_ids)
        ).all()

    db.session.add(problem_set)
    db.session.commit()

    return jsonify({
        'id': problem_set.id,
        'legacy': len(problem_set.legacy_problems),
        'coding': len(problem_set.coding_problems)
    }), 201


@bp.put('/<int:psid>')
@role_required(ROLE_TEACHER)
def update_problemset(psid):
    """
    更新题单
    """
    problem_set = ProblemSetModel.query.get(psid)
    if not problem_set:
        return jsonify({'error': 'ProblemSet not found'}), 404

    data = request.get_json()
    title = data.get('title')
    course_id = data.get('course_id')
    description = data.get('description')
    legacy_problem_ids = data.get('legacy_problem_ids', [])
    coding_problem_ids = data.get('coding_problem_ids', [])

    # 更新基础信息
    problem_set.title = title
    problem_set.description = description
    if course_id:
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 400
        problem_set.course = course

    # 更新关联题目
    problem_set.legacy_problems = LegacyProblemModel.query.filter(
        LegacyProblemModel.id.in_(legacy_problem_ids)
    ).all() if legacy_problem_ids else []

    problem_set.coding_problems = CodingProblemModel.query.filter(
        CodingProblemModel.id.in_(coding_problem_ids)
    ).all() if coding_problem_ids else []

    db.session.commit()
    return jsonify({
        'id': problem_set.id,
        'legacy': len(problem_set.legacy_problems),
        'coding': len(problem_set.coding_problems)
    }), 200


@bp.get('/<int:psid>')
@role_required()
def get_problemset(psid):
    """
    查询单个题单信息
    """
    user_id = get_jwt_identity()
    problem_set = ProblemSetModel.query.get(psid)
    if not problem_set:
        return jsonify({'error': 'ProblemSet not found'}), 404

    # 基础信息
    result = {
        'id': problem_set.id,
        'title': problem_set.title,
        'description': problem_set.description,
        'timestamp': problem_set.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
        'course': {
            'id': problem_set.course.id,
            'title': problem_set.course.course_name
        } if problem_set.course else {},
        'legacy_problems': [],
        'coding_problems': []
    }

    # 题目列表及用户提交状态
    for problem in problem_set.legacy_problems:
        submission = SubmissionModel.query.filter_by(
            user_id=user_id,
            problem_id=problem.id,
            problem_set_id=problem_set.id
        ).first()
        result['legacy_problems'].append({
            'id': problem.id,
            'title': problem.title,
            'status': submission.status.value if submission else None,
            'score': submission.score if submission else None
        })

    for problem in problem_set.coding_problems:
        submission = SubmissionModel.query.filter_by(
            user_id=user_id,
            problem_id=problem.id,
            problem_set_id=problem_set.id
        ).first()
        result['coding_problems'].append({
            'id': problem.id,
            'title': problem.title,
            'status': submission.status.value if submission else None,
            'score': submission.score if submission else None
        })

    return jsonify(result), 200


@bp.delete('/')
@role_required(ROLE_TEACHER)
def delete_problemsets():
    """
    批量删除题单
    """
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': '必须提供要删除的题单ID列表'}), 400

    deleted_count = 0
    failed = []

    for psid in ids:
        problem_set = ProblemSetModel.query.get(psid)
        if not problem_set:
            failed.append({'id': psid, 'error': 'ProblemSet not found'})
        else:
            db.session.delete(problem_set)
            deleted_count += 1

    db.session.commit()

    return jsonify({
        'deleted': deleted_count,
        'failed': failed
    }), 200


@bp.get('/')
@role_required()
def get_problemsets():
    """
    获取题单列表
    支持分页和可选课程过滤
    query 参数:
        page: 页码，默认 1
        per_page: 每页条数，默认 20
        course_id: 可选，过滤特定课程
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    course_id = request.args.get('course_id')

    query = ProblemSetModel.query
    if course_id:
        query = query.filter_by(course_id=course_id)

    pagination = query.order_by(ProblemSetModel.time_stamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    problemsets_list = []
    for ps in pagination.items:
        problemsets_list.append({
            'id': ps.id,
            'title': ps.title,
            'description': ps.description,
            'timestamp': ps.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            'course': {
                'id': ps.course.id,
                'title': ps.course.course_name,
            } if ps.course else None,
            'num_legacy_problems': len(ps.legacy_problems),
            'num_coding_problems': len(ps.coding_problems),
        })

    return jsonify({
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'problemsets': problemsets_list
    }), 200
