from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db
from .routes import api
from config.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置 JSON 响应
    app.json.ensure_ascii = False  # 确保 JSON 响应使用中文而不是 Unicode 编码
    
    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    
    # 注册蓝图
    app.register_blueprint(api, url_prefix='/api')
    
    # 创建数据库表（如果不存在）
    with app.app_context():
        db.create_all()
    
    return app 