from flask import Flask
from exts import db, jwt
from flask_migrate import Migrate
import config
from flask_cors import  CORS
from api import register_blueprints
# from datetime import timedelta

app = Flask(__name__)
app.config.from_object(config)
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=1)
db.init_app(app)
jwt.init_app(app)

migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://121.249.151.214:5173"]}})

# 注册蓝图
register_blueprints(app)
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
