from exts import db
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid

class AdminModel(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    token_version = db.Column(db.String(100), default=uuid.uuid4())
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "username": self.username,
            "timestamp": self.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class TeacherModel(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(200), nullable=True)
    profession = db.Column(db.String(200), nullable=True)
    token_version = db.Column(db.String(100), default=uuid.uuid4())
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    courses = db.relationship(
        "CourseModel",
        secondary="teacher_course",
        back_populates="teachers",
        # cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "username": self.username,
            "timestamp": self.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
            'school': self.school,
            "profession": self.profession,
            "courses": [
                {"id": course.id, "name": course.course_name}
                for course in self.courses
            ]
        }

class StudentModel(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 主键
    uid = db.Column(db.String(64), unique=True, nullable=False) # 用户 UID
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(200), nullable=True)
    profession = db.Column(db.String(200), nullable=True)
    token_version = db.Column(db.String(100), default=uuid.uuid4())
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    courses = db.relationship(
        "CourseModel",
        secondary="student_course",
        back_populates="students",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "username": self.username,
            "timestamp": self.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
            'school': self.school,
            "profession": self.profession,
            "courses": [
                {"id": course.id, "name": course.course_name}
                for course in self.courses
            ]
        }

model_mapping = {0 : AdminModel, 1 : TeacherModel, 2 : StudentModel}

class CourseModel(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(200), nullable=False)
    course_description = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    problemsets = db.relationship('ProblemSetModel', back_populates='course')

    students = db.relationship(
        "StudentModel",
        secondary="student_course",
        back_populates="courses"
    )

    teachers = db.relationship(
        "TeacherModel",
        secondary="teacher_course",
        back_populates="courses"
    )

class ProblemSetModel(db.Model):
    __tablename__ = 'problemset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())
    course = db.relationship('CourseModel', back_populates='problemsets')
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

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

    problemsets = db.relationship(
        "ProblemSetModel",
        secondary="problemset_codingproblem",
        back_populates="coding_problems"
    )

class SubmissionStatus(Enum):
    Pending = "Pending"                # 刚提交，还未判
    Judging = "Judging"                # 判题中（主要用于 Coding）
    AC = "AC"              # AC
    WA = "WA"        # WA
    CE = "CE"      # 编译错误（Coding 特有）
    TLE = "TLE"  # TLE
    MLE = "MLE"  # MLE
    RE = "RE"      # RE (99.9% Segmentation Fault)
    WrongFormat = "WrongFormat"        # 格式错误
    OLE = "OLE"  # 输出超限

class SubmissionModel(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    problem_set_id = db.Column(db.Integer, db.ForeignKey("problemset.id"), nullable=False)
    problem_id = db.Column(db.Integer, nullable=False)  # LegacyProblem 或 CodingProblem 的 ID
    problem_type = db.Column(db.Enum('legacy', 'coding'), nullable=False)
    user_answer = db.Column(db.JSON)  # 用户答案，Legacy题可以直接存选择，Coding题存代码
    score = db.Column(db.Float)  # 判题结果得分
    status = db.Column(db.Enum(SubmissionStatus), default='pending')
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

    # 关联用户
    user = db.relationship("StudentModel", backref=db.backref("submissions", lazy=True))
    # 关联题单
    problem_set = db.relationship("ProblemSetModel", backref=db.backref("submissions", lazy=True))

# 学生和课程
student_course = db.Table(
    "student_course",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)

# 教师和课程
teacher_course = db.Table(
    "teacher_course",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)

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