from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from decorators import ROLE_TEACHER, role_required
from exts import db
from models import UserModel, GroupModel, ProblemSetModel

bp = Blueprint("groups", __name__, url_prefix="/api/groups")


def is_related(user, course_id):
    """判断用户是否和课程相关"""
    return any(c.id == course_id for c in user.courses)


@bp.post("")
@role_required(ROLE_TEACHER)
def create_group():
    """教师在自己课程下创建组"""
    data = request.get_json()
    course_id = int(data.get("course_id"))
    group_name = data.get("name")
    description = data.get("description", "")

    if not course_id or not group_name:
        return jsonify({"error": "course_id and group_name is required"}), 400

    user = UserModel.query.get(get_jwt_identity())
    if not is_related(user, course_id):
        return jsonify({"error": "Permission denied"}), 403

    group = GroupModel(group_name=group_name, group_description=description, course_id=course_id)
    db.session.add(group)
    db.session.commit()

    return jsonify({
        "success": True,
        "group": {
            "id": group.id,
            "name": group_name,
            "description": description,
            "course_id": course_id,
        }}), 200


@bp.delete("")
@role_required(ROLE_TEACHER)
def delete_groups():
    """教师删除组"""
    data = request.get_json()
    group_ids = data.get("group_ids", [])
    if not group_ids:
        return jsonify({"error": "Array group_ids is required"}), 400

    user = UserModel.query.get(get_jwt_identity())
    success_cnt = 0
    results = []

    for group_id in group_ids:
        g = GroupModel.query.get(group_id)
        if not g:
            results.append({"id": group_id, "status": "fail", "error": "Group not found"})
            continue

        if not is_related(user, g.course_id):
            results.append({"id": g.id, "name": g.group_name, "status": "fail", "error": "permission denied"})
            continue

        db.session.delete(g)
        success_cnt += 1
        results.append({"id": g.id, "name": g.group_name, "status": "success"})

    db.session.commit()
    status = 200 if success_cnt == len(group_ids) else 207
    return jsonify({"success": status == 200, "results": results}), status


@bp.put("/<int:group_id>")
@role_required(ROLE_TEACHER)
def update_group(group_id):
    """教师给组分配学生和题单"""
    data = request.get_json()
    student_ids = data.get("student_ids", [])
    problemset_ids = data.get("problemset_ids", [])  # 新增字段：要绑定的题单

    group = GroupModel.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404

    user = UserModel.query.get(get_jwt_identity())
    if not is_related(user, group.course_id):
        return jsonify({"error": "Permission denied"}), 403

    # 分配学生
    if student_ids:
        students = UserModel.query.filter(
            UserModel.id.in_(student_ids),
            UserModel.usertype == "student"
        ).all()
        group.students = students

    # 绑定题单
    if problemset_ids:
        problemsets = ProblemSetModel.query.filter(
            ProblemSetModel.id.in_(problemset_ids),
            ProblemSetModel.course_id == group.course_id  # 确保题单属于同一课程
        ).all()
        group.problemsets = problemsets

    db.session.commit()

    return jsonify({
        "success": True,
        "students": [s.to_dict() for s in group.students],
        "problemsets": [{"id": ps.id, "title": ps.title} for ps in group.problemsets]
    }), 200


@bp.get("")
@role_required()
def get_groups():
    """查询自己相关课程下的组"""
    course_id = request.args.get("course_id", type=int)
    user = UserModel.query.get(get_jwt_identity())

    if user.usertype == "teacher":
        # 教师可以看到自己授课的课程下的所有组
        course_ids = [c.id for c in user.courses]
        query = GroupModel.query.filter(GroupModel.course_id.in_(course_ids))
    else:
        # 学生只能看到自己加入的组
        query = GroupModel.query.join(GroupModel.students).filter(UserModel.id == user.id)

    if course_id:
        if user.usertype == "teacher" and course_id not in course_ids:
            return jsonify({"error": "Permission denied"}), 403
        elif user.usertype != "teacher" and not any(g.course_id == course_id for g in user.groups):
            return jsonify({"error": "Permission denied"}), 403
        query = query.filter(GroupModel.course_id == course_id)

    groups = query.all()
    return jsonify({
        "groups": [
            {
                "id": g.id,
                "name": g.group_name,
                "description": g.group_description,
                "course_id": g.course_id,
                "students": len(g.students)
            } for g in groups
        ]
    })


@bp.get("/<int:group_id>")
@role_required()
def get_group(group_id):
    """组信息详情"""
    group = GroupModel.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404

    user = UserModel.query.get(get_jwt_identity())

    if user.usertype == "teacher":
        # 教师需要和课程相关
        if not is_related(user, group.course_id):
            return jsonify({"error": "Permission denied"}), 403
    else:
        # 学生必须属于该组
        if group not in user.groups:
            return jsonify({"error": "Permission denied"}), 403

    return jsonify({
        "id": group.id,
        "name": group.group_name,
        "description": group.group_description,
        "course": {
            "id": group.course.id,
            "name": group.course.course_name
        },
        "students": [s.to_dict() for s in group.students],
        "problemsets": [{"title": ps.title, "id": ps.id} for ps in group.problemsets]
    }), 200

