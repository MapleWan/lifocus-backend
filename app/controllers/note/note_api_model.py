from app.controllers import note_ns
from flask_restx import fields

note_model = note_ns.model('Note', {
    'id': fields.Integer(required=True, description='笔记id'),
    'project_id': fields.Integer(required=True, description='项目id'),
    'type': fields.String(required=True, description='笔记类型'),
    'title': fields.String(required=True, description='笔记标题'),
    'content': fields.String(required=True, description='笔记内容'),
    'folder': fields.String(required=True, description='笔记文件夹'),
    'status': fields.String(required=True, description='笔记状态'),
    'is_archived': fields.Boolean(required=True, description='是否归档'),
    'is_recycle': fields.Boolean(required=True, description='是否回收'),
    'is_share': fields.Boolean(required=True, description='是否共享'),
    'share_password': fields.String(required=True, description='共享密码'),
    'created_at': fields.String(required=True, description='创建时间'),
    'updated_at': fields.String(required=True, description='更新时间'),
})

note_response_model = note_ns.model('NoteResponseModel', {
    'code': fields.Integer(required=True, description='状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.Nested(note_model, allow_null=True),
})

# 新增笔记需要的参数
note_add_request_model = note_ns.model('NoteAddRequestModel', {
    'type': fields.String(required=True, description='笔记类型'),
    'title': fields.String(required=True, description='笔记标题'),
    'content': fields.String(required=True, description='笔记内容'),
    'folder': fields.String(required=False, description='笔记文件夹'),
    'status': fields.String(required=False, description='笔记状态'),
    'is_archived': fields.Boolean(required=False, description='是否归档'),
    'is_recycle': fields.Boolean(required=False, description='是否回收'),
    'is_share': fields.Boolean(required=False, description='是否共享'),
    'share_password': fields.String(required=False, description='共享密码'),
})

# 更新笔记需要的参数
note_update_request_model = note_ns.model('NoteUpdateRequestModel', {
    'type': fields.String(required=False, description='笔记类型'),
    'title': fields.String(required=False, description='笔记标题'),
    'content': fields.String(required=False, description='笔记内容'),
    'folder': fields.String(required=False, description='笔记文件夹'),
    'status': fields.String(required=False, description='笔记状态'),
    'is_archived': fields.Boolean(required=False, description='是否归档'),
    'is_recycle': fields.Boolean(required=False, description='是否回收'),
    'is_share': fields.Boolean(required=False, description='是否共享'),
    'share_password': fields.String(required=False, description='共享密码'),
})

# 删除笔记返回
note_delete_response_model = note_ns.model('NoteDeleteResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
})

note_response_list_model = note_ns.model('NoteResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'data': fields.List(fields.Nested(note_model), allow_null=True),
})

note_page_model = note_ns.model('NotePageModel', {
    'total': fields.Integer(required=True, description='总条数'),
    'pages': fields.Integer(required=True, description='总页数'),
    'page_no': fields.Integer(required=True, description='当前页码'),
    'page_size': fields.Integer(required=True, description='每页数量'),
    'data': fields.List(fields.Nested(note_model), allow_null=True)
})
note_page_request_model = note_ns.model('NotePageRequestModel', {
    'query': fields.Nested(note_model, required=False, allow_null=True, description='查询条件'),
    'page_no': fields.Integer(required=False, description='页码'),
    'page_size': fields.Integer(required=False, description='每页数量')
})
note_page_response_model = note_ns.model('NotePageResponseModel', {
    'code': fields.Integer(required=True, description='自定义状态码'),
    'message': fields.String(required=True, description='返回信息'),
    'page_data': fields.Nested(note_page_model, allow_null=True, description='分页数据')
})

