from exts import db
from sqlalchemy.sql import func
from datetime import datetime
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

model_mapping = {0 : AdminModel, 1 : TeacherModel, 2 : StudentModel}

class CourseModel(db.Model):
	__tablename__ = 'course'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	course_name = db.Column(db.String(200), nullable=False)
	course_description = db.Column(db.Text)
	time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=func.now())

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


student_course = db.Table(
    "student_course",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)

# 关联表：教师和课程（多对多）
teacher_course = db.Table(
    "teacher_course",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)
