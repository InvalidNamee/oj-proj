from flask_jwt_extended import get_jwt
from datetime import datetime

def is_admin():
    return get_jwt()['login_type'] == 'admin'

def is_related(user, course_id):
    """判断用户是否和课程相关"""
    return is_admin() or any(c.id == course_id for c in user.courses)

def can_access_problemset(user, problemset):
    # 教师或助教等非学生用户直接放行
    if user.usertype != 'student':
        return True

    # 学生：必须在自己所在分组，并且时间符合要求
    now = datetime.now()
    in_group = problemset.group_id in [g.id for g in user.groups]
    in_time = (problemset.start_time is None or problemset.start_time <= now) and \
              (problemset.end_time is None or now <= problemset.end_time)

    return in_group and in_time