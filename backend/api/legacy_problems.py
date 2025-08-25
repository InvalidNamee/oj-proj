# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import get_jwt_identity, get_jwt
# from modules.verify import is_admin
# from exts import db
# from models import ProblemModel, UserModel, CourseModel
# from decorators import role_required, ROLE_TEACHER, ROLE_ADMIN
#
# bp = Blueprint('legacy_problems', __name__, url_prefix='/api/legacy_problems')
#
# @bp.post('/legacy')
# @role_required(ROLE_TEACHER)
# def create_legacy():
#     problem_list = request.get_json().get('problem_list', [])
#     user = UserModel.query.get(get_jwt_identity())
#     results, success_cnt = [], 0
#
#     for problem in problem_list:
#         problem_type = problem.get('problem_type')
#         title = problem.get('title')
#         description = problem.get('description')
#         options = problem.get('options')
#         answers = problem.get('answers')
#         course_id = problem.get('course_id')
#
#         course = CourseModel.query.get(course_id)
#         if course is None:
#             results.append({'title': title, 'status': 'fail', 'error': f'Course {course_id} not found'})
#             continue
#
#         if not is_admin() and course_id not in [c.id for c in user.courses]:
#             results.append({'title': title, 'status': 'fail', 'error': f'Course {course_id}: Permission denied'})
#             continue
#
#         problem = LegacyProblemModel(
#             problem_type=problem_type,
#             title=title,
#             description=description,
#             options=options,
#             answers=answers,
#             course=course
#         )
#         db.session.add(problem)
#         db.session.flush()
#         results.append({'title': title, 'status': 'success'})
#         success_cnt += 1
#
#     db.session.commit()
#     status = 201 if success_cnt == len(problem_list) else 207 if success_cnt else 400
#     return jsonify({'success': success_cnt, 'results': results}), status
#
#
# @bp.put('/<int:pid>')
# @role_required(ROLE_TEACHER)
# def update_legacy_problem(pid):
#     user = UserModel.query.get(get_jwt_identity())
#     problem = LegacyProblemModel.query.get(pid)
#     if not problem:
#         return jsonify({'error': 'Problem not found'}), 404
#
#     if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
#         return jsonify({'error': 'Permission denied'}), 403
#
#     data = request.get_json()
#     course_id = data.get('course_id')
#
#     course = CourseModel.query.get(course_id)
#     if not course:
#         return jsonify({'error': 'Course not found'}), 404
#
#     if not is_admin() and course.id not in [c.id for c in user.courses]:
#         return jsonify({'error': 'Permission denied'}), 403
#
#     problem.title = data.get('title')
#     problem.description = data.get('description')
#     problem.options = data.get('options')
#     problem.answers = data.get('answers')
#     problem.course = course
#     db.session.commit()
#     return jsonify({'success': True}), 200
#
#
# @bp.delete('/')
# @role_required(ROLE_TEACHER)
# def delete_legacy_problems():
#     """
#     批量删除
#     """
#     user = UserModel.query.get(get_jwt_identity())
#     problem_ids = request.get_json().get('problem_ids', [])
#     success_cnt, results = 0, []
#
#     for problem_id in problem_ids:
#         problem = LegacyProblemModel.query.get(problem_id)
#         if problem is None:
#             results.append({'id': problem_id, 'status': 'fail', 'error': 'Problem not found'})
#             continue
#
#         if not is_admin() and problem.course_id not in [c.id for c in user.courses]:
#             results.append({'id': problem_id, 'status': 'fail', 'error': 'Permission denied'})
#             continue
#
#         db.session.delete(problem)
#         results.append({'id': problem_id, 'status': 'success'})
#         success_cnt += 1
#
#     db.session.commit()
#     status = 200 if success_cnt == len(problem_ids) else 207 if success_cnt else 400
#     return jsonify({'success': success_cnt, 'results': results}), status
#
