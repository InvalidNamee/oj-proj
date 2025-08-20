from flask import Flask
from exts import db, jwt
from flask_migrate import Migrate
import config # 配置文件
from flask_cors import  CORS
from api import register_blueprints

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
jwt.init_app(app)

migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

# 注册蓝图
register_blueprints(app)
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
