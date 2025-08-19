"""
和课程分配相关
"""
from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import get_jwt_identity, get_jwt
from decorators import role_required, ROLE_TEACHER, ROLE_ADMIN
from models import UserModel, CourseModel
from exts import db

bp = Blueprint("course", __name__, url_prefix="/api")

@bp.post('/user_list')
# @role_required(ROLE_TEACHER)
def user_list():
    """
    获取用户列表（JSON 请求体）
    支持查询：
    - usertype: teacher=教师, student=学生
    - uid: 学号/工号关键字
    - username: 用户名关键字
    - school / profession
    - course_ids: 课程 id 列表
    - page / per_page: 分页
    """
    data = request.get_json() or {}

    usertype = data.get('usertype')
    uid_keyword = data.get('uid')
    username_keyword = data.get('username')
    school = data.get('school')
    profession = data.get('profession')
    course_ids = data.get('course_ids', [])
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)

    query = UserModel.query

    # 查询用户类别
    if usertype:
        query = query.filter(UserModel.usertype == usertype)

    # 模糊查询 uid / username
    if uid_keyword:
        query = query.filter(UserModel.uid.like(f"%{uid_keyword}%"))
    if username_keyword:
        query = query.filter(UserModel.username.like(f"%{username_keyword}%"))

    # 学校/专业（学生）
    if school and usertype == 2:
        query = query.filter(UserModel.school.like(f"%{school}%"))
    if profession and usertype == 2:
        query = query.filter(UserModel.profession.like(f"%{profession}%"))

    # 筛选课程
    if course_ids:
        query = query.join(UserModel.courses).filter(CourseModel.id.in_(course_ids))

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    users_list = [user.to_dict() for user in pagination.items]

    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'users': users_list
    }), 200


@bp.post('/modify_course')
@role_required(ROLE_TEACHER)
def modify_course():
    """
    添加 or 大改课程
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    cid = request.args.get('cid')
    data = request.get_json()
    course_name = data.get('course_name')
    course_description = data.get('course_description')
    teacher_ids = data.get('teacher_ids', [])
    student_ids = data.get('student_ids', [])

    user_ids = teacher_ids + student_ids

    if cid:
        # 修改已有课程
        course = CourseModel.query.get(cid)
        if not course:
            return jsonify({'error': '课程不存在'}), 404

        if login_type == 1 and user_id not in [t.id for t in course.teachers]:
            return jsonify({'error': '您无权修改此课程'}), 403

        course.course_name = course_name
        course.course_description = course_description
        # 清空已有关系再添加新关系
        course.users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()
        action = "修改"
    else:
        if login_type != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        # 添加新课程
        course = CourseModel(course_name=course_name, course_description=course_description)
        db.session.add(course)
        course.users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()
        action = "添加"

    db.session.commit()
    return jsonify({'success': f'成功{action} 1 个课程'}), 200

@bp.get('/course_list')
@role_required()
def course_list():
    """
    获取课程列表（分页）
    - 管理员：可查看所有课程
    - 教师/学生：只能查看与自己相关的课程
    """
    user_id = request.args.get('id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = CourseModel.query

    user = UserModel.get(user_id)
    if user is None:
        return jsonify({"error": "用户不存在"}), 404

    if user.usertype != 'admin':  # 非管理员
        query = query.join(CourseModel.users).filter_by(id=user.id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for course in pagination.items:
        data.append({
            'id': course.id,
            'name': course.name,
            'description': course.course_description,
            'timestamp': course.time_stamp,
            'teachers': [t.to_dict() for t in course.users if t.usertype == 'teacher'],
        })

    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'items': data
    }), 200

@bp.get('/course_info')
@role_required()
def course_info():
    course_id = request.args.get('id')
    if not course_id:
        return jsonify({'error': '没有传入 id 参数'}), 401
    course = CourseModel.query.get(course_id)
    if not course:
        return jsonify({'error': '课程不存在'}), 404
    users = course.users
    teachers = [user.to_dict() for user in users if user.usertype == 'teacher']
    students = [user.to_dict() for user in users if user.usertype == 'student']
    return jsonify({
        'course_name': course.course_name,
        'description': course.course_description,
        'teachers': teachers,
        'students': students
    }), 200

@bp.post('/delete_course')
@role_required(ROLE_ADMIN)
def delete_course():
    course_ids = request.get_json().get('courses')
    success, fail = 0, 0
    fail_list = []
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
