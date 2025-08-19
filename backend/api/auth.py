"""
和网站授权相关
"""
from flask import Blueprint, request, jsonify
from decorators import role_required, ROLE_ADMIN, ROLE_TEACHER
from models import UserModel, CourseModel
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import uuid

bp = Blueprint('auth', __name__, url_prefix='/api/')

def register_user(login_type, info, commit=True):
    uid = info.get('uid')
    username = info.get('username')
    password = generate_password_hash(info.get('password'))
    usertype = info.get('usertype')
    school = info.get('school')
    profession = info.get('profession')

    if login_type == 'teacher' and usertype != 'student':
        return {'error': '教师只能注册学生用户'}, 403
    elif UserModel.query.filter_by(uid=uid, usertype=usertype).first():
        return {'error': '用户 UID 已存在'}, 401
    else:
        db.session.add(
            UserModel(uid=uid, usertype=usertype, username=username, password=password, school=school, profession=profession))
        if commit:
            db.session.commit()
        return {'success': '注册成功'}, 200

@bp.post('/register')
@role_required(ROLE_TEACHER)
def register():
    """
    批量注册
    """
    login_type = get_jwt()['login_type']
    user_list = request.json.get('user_list')
    success_cnt = 0
    fail_list = []
    for user in user_list:
        res, code = register_user(login_type, user, commit=False)
        if code != 200:
            fail_list.append({'user': user, 'error': res.get('error')})
        else:
            success_cnt += 1
    db.session.commit()
    return jsonify({'success': success_cnt, 'fail': len(fail_list), 'fail_list': fail_list}), 200


@bp.post('/login')
def login():
    """
    用户登录
    """
    data = request.get_json()
    uid = data.get('uid')
    password = data.get('password')
    login_type = data.get('login_type')
    # 检查用户是否存在
    user = UserModel.query.filter_by(uid=uid, usertype=login_type).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 把用户信息加到 token 里面
    token_version = uuid.uuid4()
    # 更新 token_version
    user.token_version = token_version
    db.session.commit()
    additional_claims = {'login_type': login_type, 'token_version': token_version, 'uid': user.uid, 'username': user.username}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    """
    用 refresh_token 刷新 access_token
    """
    identity = get_jwt_identity()  # 获取 refresh_token 中的用户 id
    claims = get_jwt()  # 获取 refresh_token 中的 claims

    additional_claims = {
        'login_type': claims.get('login_type'),
        'uid': claims.get('uid'),
        'username': claims.get('username'),
    }
    # 创建新 token 发给前端
    new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify(access_token=new_access_token), 200


@bp.post('/modify_info')
@role_required(ROLE_TEACHER)
def modify_info():
    """
    修改用户名和密码
    """
    user_id = get_jwt_identity()
    username = request.json.get('username')
    password = request.json.get('password')
    school = request.json.get('school')
    profession = request.json.get('profession')
    new_password = request.json.get('new_password')
    user = UserModel.query.get(user_id)
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户不存在或密码错误'}), 401
    else:
        user.username = username
        user.school = school
        user.profession = profession
        if new_password:
            user.token_version = uuid.uuid4() # 强制重登
            user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': '修改成功'}), 200

@bp.post('/modify_user')
@role_required(ROLE_TEACHER)
def modify_user():
    """
    批量修改用户信息
    """
    login_type = get_jwt()['login_type']
    data_list = request.get_json().get('user_list', [])

    success_cnt = 0
    fail_list = []

    for data in data_list:
        target_id = data.get('id')

        user = UserModel.query.get(target_id)
        if not user:
            fail_list.append({'id': target_id, 'error': '目标用户不存在'})
            continue

        # 检查权限
        if login_type == 'teacher' and user.usertype != 'student':  # 教师只能改学生
            fail_list.append({'id': user.id, 'username': user.username, 'error': '权限不足'})
            continue


        # 修改字段
        username = data.get('username')
        school = data.get('school')
        profession = data.get('profession')
        new_password = data.get('password')  # 重置密码
        course_list = data.get('course_list', [])

        if username:
            user.username = username
        if school:
            user.school = school
        if profession:
            user.profession = profession
        if new_password:
            user.password = generate_password_hash(new_password)
            user.token_version = str(uuid.uuid4())  # 强制过期 token

        if user.usertype != 'admin':
            courses = CourseModel.query.filter(CourseModel.id.in_(course_list)).all()
            user.courses = courses

        success_cnt += 1

    db.session.commit()
    return jsonify({
        'success': success_cnt,
        'fail': len(fail_list),
        'fail_list': fail_list
    }), 200


@bp.post('/logout')
@role_required()
def logout():
    """
    处理退出登录
    """
    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    user.token_version = uuid.uuid4()
    db.session.commit()
    return jsonify({'success': '注销成功'}), 200


@bp.post('/delete_user')
@role_required(ROLE_TEACHER)
def delete_user():
    """
    批量删除
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']

    delete_list = request.json.get('delete_list')

    success_cnt = 0
    fail_list = []

    for target_id in delete_list:
        user = UserModel.query.get(target_id)

        if user is None:
            fail_list.append({'id': target_id, 'error': '用户不存在'})
            continue

        if user_id == target_id:
            fail_list.append({'id': target_id, 'error': '不能删除自己'})
            continue

        if login_type == 'teacher' and user.usertype != 'student':
            fail_list.append({'id': target_id, 'error': '越权删除'})

        success_cnt += 1
        db.session.delete(user)
    db.session.commit()
    return jsonify({
        'success': success_cnt,
        'fail': len(fail_list),
        'fail_list': fail_list
    }), 200

@bp.get('/user_info')
@role_required()
def user_info():
    user_id = request.args.get('id')
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    return jsonify(user.to_dict()), 200

