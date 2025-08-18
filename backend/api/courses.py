"""
和课程分配相关
"""
from flask import Blueprint, request, jsonify
from decorators import login_required, admin_required, teacher_required
from models import StudentModel, TeacherModel, CourseModel, model_mapping
from exts import db
from flask_jwt_extended import get_jwt_identity, get_jwt

bp = Blueprint("course", __name__, url_prefix="/api")

@bp.post('/add_course')
@admin_required
def add_course():
    data = request.get_json()
    course_name = data.get('course_name')
    teachers_uid = data.get('teachers')
    students_uid = data.get('students')

    course = CourseModel(course_name=course_name)
    teachers = TeacherModel.query.filter(TeacherModel.uid.in_(teachers_uid)).all()
    students = StudentModel.query.filter(StudentModel.uid.in_(students_uid)).all()

    course.teachers.extend(teachers)
    course.students.extend(students)

    db.session.add(course)
    db.session.commit()
    return jsonify({'success': '成功添加 1 个课程'}), 200

@bp.get('/course_list')
@login_required
def course_list():
    """
    获取课程列表（分页）
    - 管理员：可查看所有课程
    - 教师/学生：只能查看与自己相关的课程
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = CourseModel.query

    if login_type != 0:  # 非管理员
        user = model_mapping[login_type].query.get(user_id)
        if user is None:
            return jsonify({"error": "用户不存在"}), 404

        if login_type == 1:  # 教师
            query = query.join(CourseModel.teachers).filter_by(id=user.id)
        elif login_type == 2:  # 学生
            query = query.join(CourseModel.students).filter_by(id=user.id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for course in pagination.items:
        data.append({
            'id': course.id,
            'name': course.name,
            'timestamp': course.time_stamp,
            'teachers': [t.to_dict() for t in course.teachers],
            'students': [s.to_dict() for s in course.students]
        })

    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'items': data
    }), 200

@bp.get('/course_info')
@login_required
def course_info():
    course_id = request.args.get('id')
    if not course_id:
        return jsonify({'error': '没有传入 id 参数'}), 401
    course = CourseModel.query.get(course_id)
    teachers = course.teachers
    students = course.students
    return jsonify({
        'course_name': course.course_name,
        'teachers': [teacher.to_dict() for teacher in teachers],
        'students': [student.to_dict() for student in students]
    }), 200

@bp.post('/delete_course')
@admin_required
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

