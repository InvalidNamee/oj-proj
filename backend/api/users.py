"""
和用户相关
"""
from flask import Blueprint, request, jsonify
from decorators import role_required, ROLE_ADMIN, ROLE_TEACHER
from models import UserModel, CourseModel, UserCourse
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt, get_jwt_identity
import uuid

bp = Blueprint('users', __name__, url_prefix='/api/users')


def register_user(login_type, info, commit=True):
    """
    注册或更新用户
    login_type: 当前操作用户类型
    info: 字典，包含 uid, username, password, usertype, school, profession, course_list
    commit: 是否立即提交数据库
    """
    uid = info.get('uid')
    username = info.get('username')
    password = generate_password_hash(info.get('password')) if info.get('password') else None
    usertype = info.get('usertype')
    school = info.get('school')
    profession = info.get('profession')
    course_list = info.get('course_list', [])

    # 教师只能注册学生
    if login_type == 'teacher' and usertype != 'student':
        return {'error': 'Teacher accounts can only operate student accounts'}, 403

    # 查询是否存在
    user = UserModel.query.filter_by(uid=uid).first()

    if user:
        # 已存在则更新信息
        if username:
            user.username = username
        if password:
            user.password = password
            user.token_version = str(uuid.uuid4())  # 强制过期 token
        user.school = school
        user.profession = profession

    else:
        # 不存在则创建
        user = UserModel(
            uid=uid,
            username=username,
            password=password,
            usertype=usertype,
            school=school,
            profession=profession
        )
        db.session.add(user)

    # 添加课程
    if usertype != 'admin' and course_list:
        if login_type == 'teacher':
            # 教师只能选择自己有权限的课程
            teacher = UserModel.query.get(get_jwt_identity())
            available_courses = [c for c in teacher.courses if c.id in course_list]
        else:
            # 管理员可以选择任意课程
            available_courses = CourseModel.query.filter(CourseModel.id.in_(course_list)).all()

        # 并集处理（避免重复）
        user.courses = list(set(user.courses + available_courses))

    if commit:
        db.session.commit()

    return {'status': 'success', 'uid': user.uid}, 200


@bp.post('/import')
@role_required(ROLE_TEACHER)
def import_users():
    """
    批量注册用户
    """
    login_type = get_jwt()['login_type']
    user_list = request.json.get('user_list', [])

    results = []
    success_cnt = 0

    for user in user_list:
        res, code = register_user(login_type, user, commit=False)
        if code == 200:
            results.append({'status': 'success', 'user': user})
            success_cnt += 1
        else:
            results.append({'status': 'fail', 'user': user, 'error': res.get('error')})

    db.session.commit()

    http_status = 201 if success_cnt == len(user_list) else 207

    return jsonify({
        'success_count': success_cnt,
        'fail_count': len(user_list) - success_cnt,
        'results': results
    }), http_status


@bp.post('/')
@role_required(ROLE_TEACHER)
def create_user():
    """
    单独注册用户（教师可以注册学生或管理员）
    """
    login_type = get_jwt()['login_type']
    data = request.get_json()

    # 调用通用注册函数
    res, code = register_user(login_type, data, commit=True)

    if code == 200:
        return jsonify({'status': 'success', 'user': data}), 201
    else:
        return jsonify({'status': 'fail', 'user': data, 'error': res.get('error')}), 400


@bp.patch('/')
@role_required()
def change_password():
    """
    修改当前登录用户密码（可选修改其他信息）
    """
    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    password = data.get('password')
    new_password = data.get('new_password')

    if not password or not check_password_hash(user.password, password):
        return jsonify({'error': 'Wrong password'}), 401

    user.password = generate_password_hash(new_password)
    user.token_version = str(uuid.uuid4())  # 强制过期所有 token

    db.session.commit()
    return jsonify({'success': True}), 200


@bp.delete('/')
@role_required(ROLE_ADMIN)
def delete_users():
    """
    Batch delete users.
    Request JSON: { "user_ids": [1,2,3,...] }
    """
    current_user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    user_ids = request.json.get('user_ids', [])

    if not user_ids:
        return jsonify({'error': 'User ID list is required'}), 400

    results = []
    success_cnt = 0

    for uid in user_ids:
        user = UserModel.query.get(uid)
        if not user:
            results.append({'id': uid, 'status': 'fail', 'error': 'User not found'})
            continue

        if uid == current_user_id:
            results.append({'id': uid, 'status': 'fail', 'error': 'Cannot delete yourself'})
            continue

        if login_type == 'teacher' and user.usertype != 'student':
            results.append({'id': uid, 'status': 'fail', 'error': 'Insufficient permissions'})
            continue

        db.session.delete(user)
        results.append({'id': uid, 'status': 'success'})
        success_cnt += 1

    db.session.commit()

    status_code = 200 if success_cnt == len(user_ids) else 207

    return jsonify({
        'total': len(user_ids),
        'success': success_cnt,
        'fail': len(user_ids) - success_cnt,
        'results': results
    }), status_code


@bp.get('/<int:user_id>')
@role_required()
def get_user(user_id):
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200


@bp.get('/')
@role_required()
def get_users():
    """
    分页 + 条件筛选用户
    - 普通用户：只能看到和自己有公共课程的用户
    - 管理员（没有绑定课程但有全局权限的角色）：可以看到所有用户
    - 可以通过传入 course_id 筛选某个课程下的用户（前提是有权限）
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 当前登录用户
    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)

    # 当前用户的课程 id 列表
    my_courses = [
        uc.course_id for uc in UserCourse.query.filter_by(user_id=user.id).all()
    ]

    # 基础查询
    query = UserModel.query

    # 是否要求筛选某个课程
    course_id = request.args.get('course_id')
    if course_id:
        # 检查权限：只有当用户在该课程里，或者是全局管理员，才能查
        if course_id not in my_courses and user.usertype != 'admin':
            return jsonify({'error': 'No permission to view this course users'}), 403

        query = (
            query.join(UserCourse, UserModel.id == UserCourse.user_id)
            .filter(UserCourse.course_id == course_id)
        )

    else:
        # 没指定 course_id
        if not my_courses and user.usertype == 'admin':
            # 管理员，没绑定课程，也能看所有人
            pass
        else:
            # 普通用户，只能看有交集课程的人
            sub_courses = (
                db.session.query(UserCourse.course_id)
                .filter(UserCourse.user_id == user.id)
                .subquery()
            )
            query = (
                query.join(UserCourse, UserModel.id == UserCourse.user_id)
                .filter(UserCourse.course_id.in_(sub_courses))
                .distinct()
            )

    username = request.args.get('username')
    usertype = request.args.get('usertype')
    school = request.args.get('school')
    profession = request.args.get('profession')

    # 条件筛选
    if username:
        query = query.filter(UserModel.username.ilike(f"%{username}%"))

    if usertype:
        query = query.filter(UserModel.usertype == usertype)

    if school:
        query = query.filter(UserModel.school.ilike(f"%{school}%"))

    if profession:
        query = query.filter(UserModel.profession.ilike(f"%{profession}%"))

    # 分页
    pagination = query.order_by(UserModel.time_stamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = [u.to_dict() for u in pagination.items]

    return jsonify({
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "users": users
    })
