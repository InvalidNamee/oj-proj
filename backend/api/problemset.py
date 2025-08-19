from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import CourseModel, LegacyProblemModel, CodingProblemModel, ProblemSetModel, SubmissionModel, SubmissionStatus
from decorators import role_required, ROLE_ADMIN, ROLE_TEACHER

bp = Blueprint('problemset', __name__, url_prefix='/api')

def legacy_judger(problem_type, answers, user_answers):
    if problem_type == 'single':
        # 单选
        if answers == user_answers:
            return 100, SubmissionStatus.AC
        else:
            return 0, SubmissionStatus.WA
    elif problem_type == 'multiple':
        # 多选
        if answers == user_answers:
            return 100, SubmissionStatus.AC
        elif set(user_answers).issubset(set(answers)):
            return 1, SubmissionStatus.WA
        else:
            return 0, SubmissionStatus.WA
    elif problem_type == 'fill':
        if answers == user_answers:
            return 100, SubmissionStatus.AC
        else:
            return 0, SubmissionStatus.WA
    else:
        return 0, SubmissionStatus.WA


@bp.post('/import_legacy_problems')
@role_required(ROLE_TEACHER)
def import_legacy_problems():
    problem_list = request.get_json().get('problem_list')
    for problem in problem_list:
        problem_type = problem.get('problem_type')
        title = problem.get('title')
        description = problem.get('description')
        options = problem.get('options')
        answers = problem.get('answers')
        db.session.add(LegacyProblemModel(problem_type=problem_type, title=title, description=description, options=options, answers=answers))
    db.session.commit()
    return jsonify({'success': '成功'}), 200

@bp.post('/delete_legacy_problems')
@role_required(ROLE_TEACHER)
def delete_legacy_problems():
    """
    批量删除
    """
    problem_id_list = request.get_json().get('problem_id_list')
    success_cnt = 0
    fail_list = []
    for problem_id in problem_id_list:
        problem = LegacyProblemModel.query.get(problem_id)
        if problem is None:
            fail_list.append({'id': problem_id, 'error': 'Problem not found'})
            continue
        db.session.delete(problem)
        success_cnt += 1
    db.session.commit()
    return jsonify({'success': success_cnt, 'fail': len(fail_list), 'fail_list': fail_list}), 200



@bp.post('/modify_problemset')
@role_required(ROLE_TEACHER)
def modify_problemset():
    """
    新建 / 更新题单
    还没考虑并发 ！！！
    """
    data = request.get_json()
    psid = data.get('psid')
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

    if not psid:
        problem_set = ProblemSetModel()
        db.session.add(problem_set)
    else:
        problem_set = ProblemSetModel.query.get(psid)
        if not problem_set:
            return jsonify({'error': 'ProblemSet not found'}), 404

    problem_set.course = course
    problem_set.title = title
    problem_set.description = description


    legacy_problems = LegacyProblemModel.query.filter(
        LegacyProblemModel.id.in_(legacy_problem_ids)
    ).all() if legacy_problem_ids else []

    coding_problems = CodingProblemModel.query.filter(
        CodingProblemModel.id.in_(coding_problem_ids)
    ).all() if coding_problem_ids else []

    problem_set.legacy_problems = legacy_problems
    problem_set.coding_problems = coding_problems

    db.session.commit()
    return jsonify({'legacy': len(legacy_problems), 'coding': len(coding_problems)}), 200

@bp.get('/problemset_info')
@role_required()
def problemset_info():
    """
    查询题单信息
    """
    psid = request.args.get('id')
    if not psid:
        return jsonify({'error': '需要传入id'}), 400
    problem_set = ProblemSetModel.query.get(psid)
    if not problem_set:
        return jsonify({'error': 'ProblemSet not found'}), 404
    title = problem_set.title
    description = problem_set.description
    timestamp = problem_set.time_stamp
    course = problem_set.course
    legacy_problems = problem_set.legacy_problems
    coding_problems = problem_set.coding_problems
    return jsonify({
        'title': title,
        'description': description,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'course': {
            'id': course.id,
            'title': course.course_name,
        } if course else {},
        'legacy_problems': [{'id': problem.id, 'title': problem.title} for problem in legacy_problems],
        'coding_problems': [{'id': problem.id, 'title': problem.title} for problem in coding_problems],
    })

@bp.post('/delete_problemset')
@role_required(ROLE_TEACHER)
def delete_problemset():
    """
    批量删除
    """
    data = request.get_json()
    psid_list = data.get('psid_list')
    success_cnt = 0
    fail_list = []
    for psid in psid_list:
        problem_set = ProblemSetModel.query.get(psid)
        if not problem_set:
            fail_list.append({'id': psid, 'error': 'ProblemSet not found'})
        else:
            db.session.delete(problem_set)
            success_cnt += 1
    db.session.commit()
    return jsonify({'success': success_cnt, 'fail': len(fail_list), 'fail_list': fail_list}), 200


@bp.post('/judge_legacy')
@role_required()
def judge_legacy():
    """
    判 Legacy 题
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    problem_set_id = data.get('problem_set_id')
    problem_id = data.get('problem_id')
    user_answers = data.get('user_answers')

    if problem_id is None or user_answers is None:
        return jsonify({'error': 'Missing problem_id or user_answers'}), 400

    # 获取题目
    problem = LegacyProblemModel.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # 调用已有 judge 函数
    score, status = legacy_judger(problem.problem_type, problem.answers, user_answers)

    # 记录提交（先做简单示例，之后再和题单关联）
    submission = SubmissionModel(
        user_id=user_id,
        problem_set_id=problem_set_id,
        problem_id=problem_id,
        problem_type='legacy',
        user_answer=user_answers,
        score=score,
        status=status.value
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({'score': score, 'status': status.value}), 200