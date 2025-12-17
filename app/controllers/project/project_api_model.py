from app.controllers import project_ns
from flask_restx import fields

project_model = project_ns.model('ProjectModel', {
    'id': fields.Integer(required=False, description='项目ID'),
    'type': fields.String(required=True, description='项目类型'),
    'name': fields.String(required=True, description='项目名称'),
    'icon': fields.String(required=False, description='项目图标URL'),
    'description': fields.String(required=False, description='项目描述'),
    'folder': fields.String(required=False, description='项目文件夹'),
    'status': fields.String(required=False, description='项目状态'),
    'is_archived': fields.Boolean(required=False, description='项目是否归档'),
    'is_recycle': fields.Boolean(required=False, description='项目是否回收'),
    'is_favor': fields.Boolean(required=False, description='项目是否收藏'),
    'created_at': fields.String(required=False, description='创建时间'),
    'updated_at': fields.String(required=False, description='更新时间')
})

# 新增项目需要的参数
project_add_request_model = project_ns.model('ProjectRequestModel', {
    'type': fields.String(required=True, description='项目类型'),
    'name': fields.String(required=True, description='项目名称'),
    'icon': fields.String(required=False, description='项目图标URL'),
    'description': fields.String(required=False, description='项目描述'),
    'created_at': fields.String(required=False, description='创建时间'),
    'updated_at': fields.String(required=False, description='更新时间')
})

# 更新项目所需参数
project_update_request_model = project_ns.model('ProjectUpdateRequestModel', {
    'type': fields.String(required=False, description='项目类型'),
    'name': fields.String(required=False, description='项目名称'),
    'icon': fields.String(required=False, description='项目图标URL'),
    'description': fields.String(required=False, description='项目描述'),
    'folder': fields.String(required=False, description='项目文件夹'),
    'status': fields.String(required=False, description='项目状态'),
    'is_archived': fields.Boolean(required=False, description='项目是否归档'),
    'is_recycle': fields.Boolean(required=False, description='项目是否回收'),
    'is_favor': fields.Boolean(required=False, description='项目是否收藏')
})

project_response_model = project_ns.model('ProjectAddResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.Nested(project_model, allow_null=True)
})

# 返回的项目信息
project_response_list_model = project_ns.model('ProjectResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.List(fields.Nested(project_model), allow_null=True)
})

project_delete_response_model = project_ns.model('ProjectDeleteResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息')
})
