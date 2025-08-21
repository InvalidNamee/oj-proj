from flask_jwt_extended import get_jwt

def is_admin():
    return get_jwt()['login_type'] == 'admin'