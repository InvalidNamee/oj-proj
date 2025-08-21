from exts import db
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum, unique
import uuid


class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 主键
    uid = db.Column(db.String(64), unique=True, nullable=False) # 用户 UID
    usertype = db.Column(db.Enum('admin', 'teacher', 'student'), nullable=False, default='student')
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(200), nullable=True)
    profession = db.Column(db.String(200), nullable=True)
    token_version = db.Column(db.String(100), default=uuid.uuid4())
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    courses = db.relationship(
        "CourseModel",
        secondary="user_course",
        back_populates="users",
    )

    groups = db.relationship(
        "GroupModel",
        secondary="group_student",
        back_populates="students"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            'usertype': self.usertype,
            "username": self.username,
            "timestamp": self.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
            'school': self.school,
            "profession": self.profession,
            "courses": [
                {"id": course.id, "name": course.course_name}
                for course in self.courses
            ]
        }


class CourseModel(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(200), nullable=False)
    course_description = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    problemsets = db.relationship('ProblemSetModel', back_populates='course')
    groups = db.relationship('GroupModel', back_populates='course')

    users = db.relationship(
        "UserModel",
        secondary="user_course",
        back_populates="courses"
    )

class GroupModel(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(200), nullable=False)
    group_description = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('CourseModel', back_populates='groups')
    problemsets = db.relationship('ProblemSetModel', back_populates='group')

    students = db.relationship(
        "UserModel",
        secondary="group_student",
        back_populates="groups"
    )


group_student = db.Table(
    "group_student",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
    db.Column("student_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)


user_course = db.Table(
    "user_course",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True),
)

class ProblemSetModel(db.Model):
    __tablename__ = 'problemset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    # 绑定课程
    course = db.relationship('CourseModel', back_populates='problemsets')
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    # 绑定分组
    group = db.relationship('GroupModel', back_populates='problemsets')
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    # 绑定题目
    legacy_problems = db.relationship(
        "LegacyProblemModel",
        secondary="problemset_legacyproblem",
        back_populates="problemsets"
    )
    coding_problems = db.relationship(
        "CodingProblemModel",
        secondary="problemset_codingproblem",
        back_populates="problemsets"
    )


class LegacyProblemModel(db.Model):
    __tablename__ = 'legacy_problem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_type = db.Column(db.Enum('single', 'multiple', 'fill', 'subjective'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    options = db.Column(db.JSON)
    answers = db.Column(db.JSON)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    problemsets = db.relationship(
        "ProblemSetModel",
        secondary="problemset_legacyproblem",
        back_populates="legacy_problems"
    )


class CodingProblemModel(db.Model):
    __tablename__ = 'coding_problem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    test_cases = db.Column(db.JSON)
    limitations = db.Column(db.JSON)

    problemsets = db.relationship(
        "ProblemSetModel",
        secondary="problemset_codingproblem",
        back_populates="coding_problems"
    )

class SubmissionStatus(Enum):
    Pending = "Pending"           # 刚提交，还未判
    Judging = "Judging"           # 判题中（主要用于 Coding）
    AC = "AC"                     # AC
    WA = "WA"                     # WA
    CE = "CE"                     # 编译错误（Coding 特有）
    TLE = "TLE"                   # TLE
    MLE = "MLE"                   # MLE
    RE = "RE"                     # RE (99.9% Segmentation Fault)
    WrongFormat = "WrongFormat"   # 格式错误
    OLE = "OLE"                   # 输出超限

class SubmissionModel(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    problem_set_id = db.Column(db.Integer, db.ForeignKey("problemset.id"), nullable=False)
    problem_id = db.Column(db.Integer, nullable=False)  # LegacyProblem 或 CodingProblem 的 ID
    problem_type = db.Column(db.Enum('legacy', 'coding'), nullable=False)
    user_answer = db.Column(db.JSON)  # 用户答案，Legacy题可以直接存选择，Coding题存代码
    score = db.Column(db.Float)  # 判题结果得分
    status = db.Column(db.Enum(SubmissionStatus), default='pending')
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    # 关联用户
    user = db.relationship("UserModel", backref=db.backref("submissions", lazy=True))
    # 关联题单
    problem_set = db.relationship("ProblemSetModel", backref=db.backref("submissions", lazy=True))


# 题集和题目的多对多
problemset_legacyproblem = db.Table(
    "problemset_legacyproblem",
    db.Column("problemset_id", db.Integer, db.ForeignKey("problemset.id"), primary_key=True),
    db.Column("legacy_problem_id", db.Integer, db.ForeignKey("legacy_problem.id"), primary_key=True)
)

problemset_codingproblem = db.Table(
    "problemset_codingproblem",
    db.Column("problemset_id", db.Integer, db.ForeignKey("problemset.id"), primary_key=True),
    db.Column("coding_problem_id", db.Integer, db.ForeignKey("coding_problem.id"), primary_key=True)
)