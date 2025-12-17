from flask_restx import Resource, reqparse
from app.controllers import auth_ns
from app.models import User
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt, get_jwt_identity, jwt_required
from .auth_api_model import login_request_model, login_response_model

def generate_token(user_id):
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

class Login(Resource):
    @auth_ns.expect(login_request_model)
    @auth_ns.doc(description='用户登录')
    @auth_ns.marshal_with(login_response_model)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        parser.add_argument('password', type=str, required=True, help='密码不能为空')
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        try:
            user = User.getUser(data['username'])
            if user:
                true_password = user.password
                salt = user.salt
                valid = check_password_hash(true_password, salt + data['password'])
                if valid:
                    token_data = generate_token(user.id)
                    decoded_token = decode_token(token_data['access_token']) # 解析过期时间 返回给前端
                    return {
                        'code': 200,
                        'message': '登录成功',
                        'data': {
                            **token_data,
                            'expire_time': decoded_token['exp'] * 1000 # 转换成毫秒级时间戳
                        }
                    }, 200
                else:
                    return {'code': 400, 'message': '密码错误'}, 400
        except Exception as e:
            return {'code': 500, 'message': '登录失败'}, 500
        else:
            return {'code': 400, 'message': '用户不存在'}, 400

    @jwt_required(refresh=True)
    @auth_ns.doc(description='刷新token')
    @auth_ns.marshal_with(login_response_model)
    def get(self):
        current_user_id = get_jwt_identity()
        token_data = generate_token(current_user_id)
        decoded_token = decode_token(token_data['access_token'])
        return {
            'code': 200,
            'message': '刷新成功',
            'data': {
                **token_data,
                'expire_time': decoded_token['exp'] * 1000
            }
        }, 200