from app.controllers import auth_ns
from flask_restx import fields

# 注册 需要的参数
register_request_model = auth_ns.model('RegisterRequestModel', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=False, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    # 'updated_at': fields.String(required=False, description='更新时间'),
    # 'created_at': fields.String(required=False, description='创建时间')
})
# 注册成功返回的用户字段
register_response_user_model = auth_ns.model('RegisterResponseUserModel', {
    'id': fields.Integer(required=False, description='账户ID'),
    'username': fields.String(required=False, description='用户名'),
    'email': fields.String(required=False, description='邮箱'),
    'avatar': fields.String(required=False, description='用户头像URL'),
    'updated_at': fields.String(required=False, description='更新时间'),
    'created_at': fields.String(required=False, description='创建时间')
})
# 注册成功返回
register_response_model = auth_ns.model('RegisterResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.Nested(register_response_user_model, description='返回数据', allow_null=True),
})

# 登录 需要的参数
login_request_model = auth_ns.model('LoginRequestModel', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
})
# 登录成功返回的token 结构
token_model = auth_ns.model('TokenModel', {
    'access_token': fields.String(required=True, description='访问令牌'),
    'refresh_token': fields.String(required=True, description='刷新令牌'),
    'expire_time': fields.Integer(required=True, description='令牌过期时间'),
})
# 登录成功返回
login_response_model = auth_ns.model('LoginResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.Nested(token_model, description='返回数据', allow_null=True)
})

# 登出返回
logout_response_model = auth_ns.model('LogoutResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
})