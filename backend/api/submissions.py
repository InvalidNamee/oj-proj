from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import LegacyProblemModel, CodingProblemModel, ProblemSetModel, SubmissionModel
from decorators import role_required, ROLE_TEACHER
from modules.legacy_judger import legacy_judger

bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

@bp.post('/legacy')
@role_required()
def submit_legacy():
    """
    提交 Legacy 题目答案并判分
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    problem_set_id = data.get('problem_set_id')
    problem_id = data.get('problem_id')
    user_answers = data.get('user_answers')

    if not problem_id or user_answers is None:
        return jsonify({'error': 'Missing problem_id or user_answers'}), 400

    problem = LegacyProblemModel.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # 判题
    score, status = legacy_judger(problem.problem_type, problem.answers, user_answers)

    # 保存提交
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

    return jsonify({
        'problem_id': problem_id,
        'problem_set_id': problem_set_id,
        'score': score,
        'status': status.value
    }), 201

@bp.post('/coding')
@role_required()
def submit_coding():
    pass