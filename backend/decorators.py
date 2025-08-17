from models import model_mapping
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify
from functools import wraps

def login_required(f):
    @wraps(f)
    @jwt_required()
    def wrap(*args, **kwargs):
        identity = get_jwt_identity()
        login_type = get_jwt()['login_type']
        token_version = get_jwt()['token_version']
        model = model_mapping[login_type]
        user = model.query.get(identity)
        if user is None:
            return jsonify({'error': '用户不存在'}), 401
        elif user.token_version != token_version:
            return jsonify({'error': 'token 过期'}), 401
        return f(*args, **kwargs)
    return wrap
