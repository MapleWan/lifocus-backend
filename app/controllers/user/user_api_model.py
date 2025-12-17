from app.controllers import user_ns
from flask_restx import fields

user_model = user_ns.model('User', {
    'id': fields.Integer(required=False, description='账户ID'),
    'username': fields.String(required=False, description='用户名'),
    'email': fields.String(required=False, description='邮箱'),
    'avatar': fields.String(required=False, description='用户头像URL'),
    'updated_at': fields.String(required=False, description='更新时间'),
    'created_at': fields.String(required=False, description='创建时间')
})

user_list_model = user_ns.model('UserList', {
    'users': fields.List(fields.Nested(user_model))
})

get_user_by_id_response_model = user_ns.model('GetUserByIdResponse', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.Nested(user_model, allow_null=True)
})

update_user_request_model = user_ns.model('UpdateUserRequest', {
    'username': fields.String(required=False, description='用户名'),
    'email': fields.String(required=False, description='邮箱'),
    'password': fields.String(required=False, description='密码'),
    'avatar': fields.String(required=False, description='用户头像URL')
})

delete_user_response_model = user_ns.model('DeleteUserResponse', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息')
})