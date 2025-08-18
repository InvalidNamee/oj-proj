"""
和网站授权相关
"""
from flask import Blueprint, request, jsonify
from decorators import login_required, teacher_required
from models import model_mapping, CourseModel
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

    target_model = model_mapping[usertype]
    if login_type == 1 and usertype != 2:
        return {'error': '教师只能注册学生用户'}, 403
    elif target_model.query.filter_by(uid=uid).first():
        return {'error': '用户 ID 已存在'}, 401
    else:
        if usertype == 0:
            db.session.add(target_model(uid=uid, username=username, password=password))
        else:
            db.session.add(
                target_model(uid=uid, username=username, password=password, school=school, profession=profession))
        if commit:
            db.session.commit()
        return {'success': '注册成功'}, 200

@bp.post('/register')
@teacher_required
def register():
    """
    单独注册
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    model = model_mapping[login_type]

    cur_user = model.query.get(user_id)
    if cur_user is None:
        return jsonify({"error": "用户信息错误"}), 401
    data = request.get_json()
    res, code = register_user(login_type, data, commit=True)
    return jsonify(res), code

@bp.post('/quick_register')
@teacher_required
def quick_register():
    """
    快速注册
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    model = model_mapping[login_type]
    cur_user = model.query.get(user_id)
    if cur_user is None:
        return jsonify({"error": "当前用户信息错误"}), 401

    user_list = request.json.get('user_list')
    success_cnt, fail_cnt = 0, 0
    fail_list = []
    for user in user_list:
        res, code = register_user(login_type, user, commit=False)
        if code != 200:
            fail_cnt += 1
            fail_list.append({'user': user, 'error': res.get('error')})
        else:
            success_cnt += 1
    db.session.commit()
    return jsonify({'success': success_cnt, 'fail': fail_cnt, 'fail_list': fail_list}), 200


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
    model = model_mapping[login_type]
    user = model.query.filter_by(uid=uid).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户名或密码错误'}), 401
    else:
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
@login_required
def modify_info():
    """
    修改用户名和密码
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    username = request.json.get('username')
    password = request.json.get('password')
    school = request.json.get('school')
    profession = request.json.get('profession')
    new_password = request.json.get('new_password')
    model = model_mapping[login_type]
    user = model.query.get(user_id)
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户不存在或密码错误'}), 401
    else:
        user.username = username
        if get_jwt()['login_type'] != 0:
            user.school = school
            user.profession = profession
        if new_password:
            user.token_version = "qwq" # 强制重登
            user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': '修改成功'}), 200


@bp.post('/logout')
@login_required
def logout():
    """
    处理退出登录
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    model = model_mapping[login_type]
    user = model.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    user.token_version = "qwq"
    db.session.commit()
    return jsonify({'success': '注销成功'}), 200


@bp.post('/delete_user')
@login_required
def delete_user():
    """
    批量删除
    """
    user_id = get_jwt_identity()
    login_type = get_jwt()['login_type']
    model = model_mapping[login_type]
    user = model.query.get(user_id)
    if not user or login_type == 2:
        return jsonify({'error': '当前用户状态不合法'}), 403

    delete_list = request.json.get('delete_list')
    for item in delete_list:
        if login_type == 1 and item['usertype'] != 2:
            continue
        model = model_mapping[item['usertype']]
        user = model.query.filter_by(uid=item['uid']).first()
        if user and user.id != user_id:
            db.session.delete(user)
    db.session.commit()
    return jsonify({'success': '删除成功'}), 200

@bp.get('/user_info')
@login_required
def user_info():
    data = request.get_json()
    target_id = data.get('id')
    target_type = data.get('usertype')
    user = model_mapping[target_type].query.get(target_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    return jsonify(user.to_dict()), 200

