from flask import Blueprint
from flask_restx import Api, Namespace

# 创建API蓝图
api_blueprint = Blueprint('lifocus_api', __name__, url_prefix='/api')

# 创建 Flask-RESTX API 实例
api = Api(
    api_blueprint,
    doc='/docs/',
    title='Lifocus API',
    description='Lifocus API Documentation',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Token格式: Bearer <token>'
        }
    },
    security='Bearer'
)

auth_ns = Namespace('auth', description='Authentication', path='/auth')
user_ns = Namespace('user', description='User', path='/user')
project_ns = Namespace('project', description='Project', path='/project')

from app.controllers.auth import Register
from app.controllers.auth import Login
from app.controllers.auth import Logout
auth_ns.add_resource(Register, '/register')
auth_ns.add_resource(Login, '/login')
auth_ns.add_resource(Logout, '/logout')

from app.controllers.user import UserManager
user_ns.add_resource(UserManager, '/<int:user_id>')

from app.controllers.project import SingleProjectManager, UserProjectManager
project_ns.add_resource(SingleProjectManager, '/singleProject', '/singleProject/<int:project_id>')
project_ns.add_resource(UserProjectManager, '/userProject')

api.add_namespace(auth_ns)
api.add_namespace(user_ns)
api.add_namespace(project_ns)