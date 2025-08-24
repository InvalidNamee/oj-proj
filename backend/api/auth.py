"""
和网站授权相关
"""
from flask import Blueprint, request, jsonify
from decorators import role_required
from models import UserModel, CourseModel
from exts import db
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import uuid

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

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
    additional_claims = {'login_type': login_type, 'token_version': token_version}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    user_dic = user.to_dict()
    if user.usertype == "admin":
        user_dic["courses"] = [{"id": c.id, "name": c.course_name} for c in CourseModel.query.all()]
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_dic
    }), 200


@bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    """
    用 refresh_token 刷新 access_token
    """
    identity = get_jwt_identity()  # 获取 refresh_token 中的用户 id
    claims = get_jwt()  # 获取 refresh_token 中的 claims
    user = UserModel.query.get_or_404(identity)
    if user.token_version != claims.get("token_version"):
        return jsonify({"error": "Token has expired"}), 401
    additional_claims = {
        'login_type': claims.get('login_type'),
        'token_version': claims.get('token_version')
    }
    # 创建新 token 发给前端
    new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify(access_token=new_access_token), 200


@bp.post('/logout')
@role_required()
def logout():
    """
    处理退出登录
    """
    user_id = get_jwt_identity()
    user = UserModel.query.get_or_404(user_id)
    user.token_version = uuid.uuid4()
    db.session.commit()
    return jsonify({'success': '注销成功'}), 200


@bp.get('/check_token')
@jwt_required()
def check_token():
    """
    检查 token
    """
    user_id = get_jwt_identity()
    user = UserModel.query.get(user_id)
    
    if user and user.token_version == get_jwt()['token_version']:
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'msg': 'Token has expired'}), 401