from exts import db
from sqlalchemy.sql import func
from datetime import datetime
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

    problems = db.relationship("ProblemModel", back_populates="course")

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
    problems = db.relationship(
        "ProblemModel",
        secondary="problemset_problem",
        back_populates="problemsets"
    )

class ProblemModel(db.Model):
    __tablename__ = 'problem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum('single', 'multiple', 'fill', 'subjective', 'coding'), nullable=False)
    description = db.Column(db.JSON)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    test_cases = db.Column(db.JSON)
    limitations = db.Column(db.JSON)
    course = db.relationship('CourseModel', back_populates='problems')
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    problemsets = db.relationship(
        "ProblemSetModel",
        secondary="problemset_problem",
        back_populates="problems"
    )


class SubmissionModel(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    problem_set_id = db.Column(db.Integer, db.ForeignKey("problemset.id"))
    problem_id = db.Column(db.Integer, nullable=False)
    problem_type = db.Column(db.Enum('single', 'multiple', 'fill', 'subjective', 'coding'), nullable=True)
    user_answer = db.Column(db.JSON)
    language = db.Column(db.Enum('python', 'cpp'))
    score = db.Column(db.Float)
    status = db.Column(db.Enum('Pending', 'Judging', 'AC', 'WA', 'TLE', 'MLE', 'OLE', 'CE', 'RE', 'IE'), default='pending')
    max_time = db.Column(db.Integer)
    max_memory = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    extra = db.Column(db.JSON)

    # 关联用户
    user = db.relationship("UserModel", backref=db.backref("submissions", lazy=True))
    # 关联题单
    problemset = db.relationship("ProblemSetModel", backref=db.backref("submissions", lazy=True))


# 题集和题目的多对多
problemset_problem = db.Table(
    "problemset_problem",
    db.Column("problemset_id", db.Integer, db.ForeignKey("problemset.id"), primary_key=True),
    db.Column("problem_id", db.Integer, db.ForeignKey("problem.id"), primary_key=True)
)