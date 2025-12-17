from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Resource
from app.controllers import auth_ns
from app.extension import redis_client
from .auth_api_model import logout_response_model
class Logout(Resource):
    @auth_ns.doc(description="用户登出")
    @auth_ns.marshal_with(logout_response_model)
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        redis_client.set(jti, '', ex= 60 * 60) # 将token加入黑名单，同时设置清除时长：1 个小时
        return {'code': 200, 'message': '登出成功'}, 200