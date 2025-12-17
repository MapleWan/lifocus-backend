import os
from flask import Flask
from flask_cors import CORS
from .config import config
import redis
from .extension import db, migrate, jwt, redis_client
from .controllers import api_blueprint

def register_JWT_hooks(jwt):
    # 注册JWT钩子函数，用于检查token是否在黑名单中
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_in_redis = redis_client.get(jti)
        return token_in_redis is not None


def create_app(config_name):
    app = Flask("lifocus")
    app.config.from_object(config[config_name])
    db.init_app(app) # 数据库初始化
    migrate.init_app(app, db) # 数据库迁移初始化
    jwt.init_app(app) # jwt初始化
    register_JWT_hooks(jwt) # 注册JWT钩子函数

    # 初始化Redis
    redis_client.connection_pool = redis.ConnectionPool(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        password=app.config['REDIS_PASSWORD']
    )

    app.register_blueprint(api_blueprint) # 注册API蓝图

    CORS(app)
    return app

app = create_app(os.getenv('FLASK_ENV', 'development'))