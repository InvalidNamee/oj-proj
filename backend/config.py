JWT_SECRET_KEY = "your-secretkey"
# 这里是数据的相关配置
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "Pswd^123"
DATABASE = "ojproj"
SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4")
