import uuid
from flask_restx import Resource, reqparse
from werkzeug.security import generate_password_hash
from app.controllers import auth_ns
from .auth_api_model import register_request_model, register_response_model
from app.models import User
from app.utils import checkEmailFormat

class Register(Resource):
    @auth_ns.expect(register_request_model)
    @auth_ns.doc(description='用户注册')
    @auth_ns.marshal_with(register_response_model)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        parser.add_argument('email', type=str, required=False)
        parser.add_argument('password', type=str, required=True, help='密码不能为空')
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        if data['email']:
            if not checkEmailFormat(data['email']): return {'message': '邮箱格式错误'}, 400
        if User.getUser(data['username']):
            return {'code': 400, 'message': '用户名<{}>已存在'.format(data['username'])}, 400
        if User.getUser(data['email']):
            return {'code': 400, 'message': '邮箱<{}>已存在'.format(data['email'])}, 400
        try:
            data['salt'] = uuid.uuid4().hex
            data['password'] = generate_password_hash(data['salt'] + data['password'])
            user = User(**data)
            user.addUser()
            return {'code': 201, 'data':user.dict()}, 201
        except Exception as e:
            return {'code': 500, 'message': '注册失败，' + str(e)}, 500
