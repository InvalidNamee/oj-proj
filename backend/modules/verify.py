from flask_jwt_extended import get_jwt

def is_admin():
    return get_jwt()['login_type'] == 'admin'

def is_related(user, course_id):
    """判断用户是否和课程相关"""
    return is_admin() or any(c.id == course_id for c in user.courses)

def can_access_problmeset(user, problemset):
    return user.usertype != 'student' or problemset.group_id in [g.id for g in user.groups]