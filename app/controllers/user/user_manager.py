from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, reqparse
from app.controllers import user_ns
from app.models import User
from .user_api_model import get_user_by_id_response_model, update_user_request_model, delete_user_response_model
from app.utils import checkEmailFormat
from datetime import datetime
class UserManager(Resource):
    
    @jwt_required()
    @user_ns.doc(description='根据用户ID获取用户信息')
    @user_ns.marshal_with(get_user_by_id_response_model)
    # def get(self, user_id):
    #     try:
    #         user = User.getUserById(user_id)
    #         if not user:
    #             return {'code': 404, 'message': '用户不存在'}, 404
    #         return {'code': 200, 'message': '查询成功', 'data': user}, 200
    #     except Exception as e:
    #         return {'code': 500, 'message': str(e)}, 500
    def get(self):
        user_id = get_jwt_identity()
        try:
            user = User.getUserById(user_id)
            if not user:
                return {'code': 404, 'message': '用户不存在'}, 404
            return {'code': 200, 'message': '查询成功', 'data': user}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500
    @jwt_required()
    @user_ns.doc(description='更新用户信息')
    @user_ns.expect(update_user_request_model)
    @user_ns.marshal_with(get_user_by_id_response_model)
    def put(self):
        user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('email', type=str, required=False)
        parser.add_argument('password', type=str, required=False)
        parser.add_argument('avatar', type=str, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        if data['email']:
            if not checkEmailFormat(data['email']): return {'message': '邮箱格式错误'}, 400
        data['update_time'] = datetime.now()
        try:
            user = User.getUserById(user_id)
            if not user:
                return {'code': 404, 'message': '用户不存在'}, 404
            else:
                if data['username']:
                    if User.getUser(data['username']):
                        return {'code': 400, 'message': '用户名<{}>已存在'.format(data['username'])}, 400
                    user.username = data['username']
                if data['email']:
                    if User.getUser(data['email']):
                        return {'code': 400, 'message': '邮箱<{}>已存在'.format(data['email'])}, 400
                    user.email = data['email']
                if data['password']: user.password = data['password']
                if data['avatar']: user.avatar = data['avatar']
                user.updateUser()
                return {'code': 200, 'message': '更新成功', 'data': user}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @user_ns.doc(description='删除用户')
    @user_ns.marshal_with(delete_user_response_model)
    def delete(self):
        user_id = get_jwt_identity()
        try:
            user = User.getUserById(user_id)
            if not user:
                return {'code': 404, 'message': '用户不存在'}, 404
            else:
                user.deleteUser()
                return {'code': 200, 'message': '删除成功'}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500