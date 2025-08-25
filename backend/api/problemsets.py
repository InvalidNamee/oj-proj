from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import CourseModel, ProblemModel, ProblemSetModel, SubmissionModel, UserModel
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
    problem_ids = data.get('problem_ids')

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
    if problem_ids:
        problem_set.problems = ProblemModel.query.filter(
            ProblemModel.id.in_(problem_ids)
        ).all()

    db.session.add(problem_set)
    db.session.commit()

    return jsonify({
        'id': problem_set.id,
        # todo 不知道写什么
    }), 201


@bp.put('/<int:psid>')
@role_required(ROLE_TEACHER)
def update_problemset(psid):
    """
    更新题单
    """
    problemset = ProblemSetModel.query.get_or_404(psid)

    data = request.get_json()
    title = data.get('title')
    course_id = data.get('course_id')
    description = data.get('description')
    problem_ids = data.get('problem_ids')

    # 更新基础信息
    problemset.title = title
    problemset.description = description
    if course_id:
        course = CourseModel.query.get_or_404(course_id)
        problemset.course = course

    # 更新关联题目
    problemset.problems = ProblemModel.query.filter(
        ProblemModel.id.in_(problem_ids)
    ).all() if problem_ids else []

    db.session.commit()
    return jsonify({
        'id': problemset.id,
        # 'legacy': len(problem_set.legacy_problems),
        # 'coding': len(problem_set.problems)
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
        'problems': []
    }

    # 题目列表及用户提交状态
    for problem in problem_set.problems:
        submission = SubmissionModel.query.filter_by(
            user_id=user_id,
            problem_id=problem.id,
            problem_set_id=problem_set.id
        ).order_by(SubmissionModel.time_stamp.desc()).first()
        result['problems'].append({
            'id': problem.id,
            'title': problem.title,
            'status': submission.status if submission else None,
            'score': submission.score if submission else None,
            'submission_id': submission.id if submission else None
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
    query 参数:
        page: 页码，默认 1
        per_page: 每页条数，默认 20
        course_id: 可选，过滤特定课程
        keyword: 可选，筛选题单标题包含该关键字
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    course_id = request.args.get('course_id', type=int)
    keyword = request.args.get('keyword', type=str)

    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)
    course_ids = [course.id for course in user.courses]

    query = ProblemSetModel.query

    if course_id:
        if course_id not in course_ids and user.usertype != 'admin':
            return jsonify({'error': 'No permission to view this course problemsets'}), 403
        query = query.filter(ProblemSetModel.course_id == course_id)
    else:
        if not course_ids and user.usertype == 'admin':
            pass  # 管理员可以查看所有题单
        else:
            query = query.filter(ProblemSetModel.course_id.in_(course_ids))

    # 按关键字过滤
    if keyword:
        query = query.filter(ProblemSetModel.title.ilike(f'%{keyword}%'))

    pagination = query.order_by(ProblemSetModel.time_stamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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
            'num_problems': len(ps.problems),
        })

    return jsonify({
        'problemsets': problemsets_list,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'total_pages': pagination.pages
    }), 200
