import os
from datetime import timedelta

# 数据库相关配置
USERNAME = os.getenv('MYSQL_USER_NAME')
PASSWORD = os.getenv('MYSQL_USER_PASSWORD')
HOSTNAEME = os.getenv('MYSQL_HOSTNAME')
PORT = os.getenv('MYSQL_PORT')
DATABASE = os.getenv('MYSQL_DATABASE')

# 数据库连接字符串
DIALECT = 'mysql'
DRIVER = 'pymysql'

class Config(object):

    DEBUG = os.getenv('FLASK_DEBUG')
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST')
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT')

    # 配置数据库连接字符串
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4'.format(DIALECT, DRIVER, USERNAME, PASSWORD, HOSTNAEME, PORT, DATABASE)

    #JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # 1小时
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1) # 1天
    # JWT_BLOCKLIST_TOKEN_CHECKS = ['access', 'refresh'] # 检查类型

    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
class DevelopmentConfig(Config):
    DEBUG = True

class ProuctionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = ''

config = {
    'development': DevelopmentConfig,
    'production': ProuctionConfig,
    'default': DevelopmentConfig
}