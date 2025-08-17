from exts import db

class AdminModel(db.Model):
	__tablename__ = 'admin'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	uid = db.Column(db.String(64), unique=True, nullable=False)
	username = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)
	token_version = db.Column(db.String(100), default="qwq")

class TeacherModel(db.Model):
	__tablename__ = 'teacher'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	uid = db.Column(db.String(64), unique=True, nullable=False)
	username = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(200), nullable=False)
	school = db.Column(db.String(200), nullable=True)
	profession = db.Column(db.String(200), nullable=True)
	token_version = db.Column(db.String(100), default="qwq")
	# classes = db.relationship('ClassModel', backref='teacher', lazy='dynamic')

class StudentModel(db.Model):
	__tablename__ = 'student'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 主键
	uid = db.Column(db.String(64), unique=True, nullable=False) # 用户 UID
	username = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(200), nullable=False)
	# classes = db.relationship('ClassModel', backref='student', lazy='dynamic')
	school = db.Column(db.String(200), nullable=True)
	profession = db.Column(db.String(200), nullable=True)
	token_version = db.Column(db.String(100), default="qwq")

model_mapping = {0 : AdminModel, 1 : TeacherModel, 2 : StudentModel}

class ClassModel(db.Model):
	__tablename__ = 'class'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	class_name = db.Column(db.String(200), nullable=False)
	# students = db.relationship('StudentModel', backref='class', lazy='dynamic')
