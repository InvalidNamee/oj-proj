from models import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify
from functools import wraps

ROLE_ADMIN = 0
ROLE_TEACHER = 1
ROLE_STUDENT = 2

role_val = {
    'studment': ROLE_STUDENT,
    'teacher': ROLE_TEACHER,
    'admin': ROLE_ADMIN,
}

def role_required(min_role=ROLE_STUDENT):
    """要求用户至少具有 min_role 的权限"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            claims = get_jwt()
            token_version = claims['token_version']
            user = UserModel.query.get(identity)
            if user is None:
                return jsonify({'error': '用户不存在'}), 401
            elif user.token_version != token_version:
                return jsonify({'error': 'Token has expired'}), 401

            # 权限不足
            if role_val[user.usertype] > min_role:
                return jsonify({'error': '无权限访问'}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
