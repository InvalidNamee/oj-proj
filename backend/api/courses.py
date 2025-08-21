from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from models import db, CourseModel, UserModel
from decorators import role_required, ROLE_ADMIN, ROLE_TEACHER

bp = Blueprint("course", __name__, url_prefix="/api/courses")


@bp.get("")
@role_required()
def list_courses():
    """
    获取课程列表（分页）
    - 管理员：可查看所有课程
    - 教师/学生：只能查看与自己相关的课程
    """
    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = CourseModel.query
    if user.usertype != 'admin':
        query = query.join(CourseModel.users).filter(UserModel.id == user.id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for course in pagination.items:
        data.append({
            'id': course.id,
            'name': course.course_name,
            'description': course.course_description,
            'timestamp': course.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
            'teachers': [t.to_dict() for t in course.users if t.usertype == 'teacher'],
        })

    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'items': data
    }), 200


@bp.get("/<int:course_id>")
@role_required()
def get_course(course_id):
    """
    获取课程详情
    """
    user = UserModel.query.get(get_jwt_identity())
    if user.usertype != "admin" and course_id not in [course.id for course in user.courses]:
        return jsonify({'error': 'Permission Denied'}), 403

    course = CourseModel.query.get(course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404

    users = course.users
    teachers = [u.to_dict() for u in users if u.usertype == 'teacher']
    students = [u.to_dict() for u in users if u.usertype == 'student']

    return jsonify({
        'id': course.id,
        'course_name': course.course_name,
        'description': course.course_description,
        'teachers': teachers,
        'students': students
    }), 200


@bp.post("")
@role_required(ROLE_ADMIN)
def create_course():
    """
    创建课程（管理员）
    """
    data = request.get_json()
    course_name = data.get('course_name')
    course_description = data.get('course_description')
    teacher_ids = data.get('teacher_ids', [])

    course = CourseModel(course_name=course_name, course_description=course_description)
    db.session.add(course)
    course.users = UserModel.query.filter(UserModel.id.in_(teacher_ids)).all()

    db.session.commit()
    return jsonify({'success': True, 'id': course.id}), 201


@bp.put("/<int:course_id>")
@role_required(ROLE_TEACHER)
def update_course(course_id):
    """
    修改课程（管理员 / 授课教师）
    """
    user_id = int(get_jwt_identity())
    login_type = get_jwt().get('login_type')

    course = CourseModel.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # 不是管理员且不是该课程教师，禁止修改
    if login_type != 'admin' and user_id not in [t.id for t in course.users]:
        # print(login_type, user_id, [t.id for t in course.users])
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()
    course.course_name = data.get('course_name', course.course_name)
    course.course_description = data.get('course_description', course.course_description)

    teacher_ids = data.get('teacher_ids', [])
    student_ids = data.get('student_ids', [])
    user_ids = teacher_ids + student_ids
    if user_ids:
        course.users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()

    db.session.commit()
    return jsonify({'success': '课程修改成功'}), 200


@bp.delete("/<int:course_id>")
@role_required(ROLE_ADMIN)
def delete_course(course_id):
    """
    删除单个课程（管理员）
    """
    course = CourseModel.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({'success': True}), 200


@bp.delete("")
@role_required(ROLE_ADMIN)
def delete_courses():
    """
    批量删除课程（管理员）
    body: { "courses": [1, 2, 3] }
    """
    course_ids = request.get_json().get('course_ids', [])
    success, fail, fail_list = 0, 0, []

    for cid in course_ids:
        course = CourseModel.query.get(cid)
        if course:
            db.session.delete(course)
            success += 1
        else:
            fail_list.append(cid)
            fail += 1

    db.session.commit()
    return jsonify({'success': success, 'fail': fail, 'fail_list': fail_list}), 200
