from flask import Blueprint, request, jsonify
from exts import db
from models import LegacyProblemModel
from decorators import role_required, ROLE_TEACHER

bp = Blueprint('legacy_problems', __name__, url_prefix='/api/legacy_problems')

@bp.post('/import')
@role_required(ROLE_TEACHER)
def import_legacy_problems():
    problem_list = request.get_json().get('problem_list')
    results = []
    for problem in problem_list:
        problem_type = problem.get('problem_type')
        title = problem.get('title')
        description = problem.get('description')
        options = problem.get('options')
        answers = problem.get('answers')
        problem = LegacyProblemModel(problem_type=problem_type, title=title, description=description, options=options, answers=answers)
        db.session.add(problem)
        db.session.flush()
        results.append({'title': title, 'id': problem.id, 'status': 'success'})
    db.session.commit()
    return jsonify({'success': True}), 201


@bp.put('/<int:pid>')
@role_required(ROLE_TEACHER)
def update_legacy_problem(pid):
    problem = LegacyProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    else:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        options = data.get('options')
        answers = data.get('answers')
        problem.title = title
        problem.description = description
        problem.options = options
        problem.answers = answers
        db.session.commit()
        return jsonify({'success': True}), 200


@bp.delete('/')
@role_required(ROLE_TEACHER)
def delete_legacy_problems():
    """
    批量删除
    """
    problem_id_list = request.get_json().get('problem_id_list')
    success_cnt = 0
    results = []
    for problem_id in problem_id_list:
        problem = LegacyProblemModel.query.get(problem_id)
        if problem is None:
            results.append({'id': problem_id, 'status': 'fail', 'error': 'Problem not found'})
            continue
        db.session.delete(problem)
        results.append({'id': problem_id, 'status': 'success'})
        success_cnt += 1
    db.session.commit()
    if success_cnt == len(problem_id_list):
        return jsonify({'success': True, 'results': results}), 200
    return jsonify({'success': False, 'results': results}), 207


@bp.get('/<int:pid>')
@role_required()
def get_legacy_problem(pid):
    """
    查询单个选择题/填空题信息
    """
    problem = LegacyProblemModel.query.get(pid)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    return jsonify({
        'id': problem.id,
        'problem_type': problem.problem_type,
        'title': problem.title,
        'description': problem.description,
        'timestamp': problem.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
        'options': problem.options
    }), 200


@bp.get('/')
@role_required(ROLE_TEACHER)
def get_legacy_problems():
    """
    获取所有 Legacy 题目列表
    """
    problems = LegacyProblemModel.query.all()
    problem_list = []
    for p in problems:
        problem_list.append({
            'id': p.id,
            'title': p.title,
            'problem_type': p.problem_type,
            'description': p.description,
            'timestamp': p.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return jsonify({'legacy_problems': problem_list}), 200