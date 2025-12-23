from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, reqparse
from app.controllers import note_ns
from app.models import Note, Project
from .note_api_model import note_response_model, note_add_request_model, note_update_request_model, note_response_list_model, note_page_request_model, note_page_response_model
from datetime import datetime, timedelta
from app.utils import hash_password

class SingleNoteManager(Resource):
    @jwt_required()
    @note_ns.doc(description='根据笔记ID获取笔记信息')
    @note_ns.marshal_with(note_response_model)
    def get(self, note_id):
        try:
            note = Note.getNoteById(note_id)
            if not note:
                return {'code': 404, 'message': '笔记不存在'}, 404
            return {'code': 200, 'message': '查询成功', 'data': note}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @note_ns.doc(description='新增笔记')
    @note_ns.expect(note_add_request_model)
    @note_ns.marshal_with(note_response_model)
    def post(self):
        project_id = request.headers.get('X-Project-Id')
        if not project_id:
            return {'code': 400, 'message': '项目ID不能为空'}, 400
        else:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        parser.add_argument('folder', type=str, required=False)
        parser.add_argument('status', type=str, required=False)
        parser.add_argument('is_archived', type=bool, required=False)
        parser.add_argument('is_recycle', type=bool, required=False)
        parser.add_argument('is_share', type=bool, required=False)
        parser.add_argument('share_password', type=str, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        try:
            data.project_id = project_id
            if data.share_password: data.share_password = hash_password(data['share_password'])
            note = Note(**data)
            note.addNote()
            return {'code': 201, 'message': '新增成功', 'data': note}, 201
        except Exception as e:
            return {'code': 500, 'message': '新增失败，' + str(e)}, 500

    @jwt_required()
    @note_ns.doc(description='更新笔记信息')
    @note_ns.expect(note_update_request_model)
    @note_ns.marshal_with(note_response_model)
    def put(self, note_id):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=False)
        parser.add_argument('title', type=str, required=False)
        parser.add_argument('content', type=str, required=False)
        parser.add_argument('folder', type=str, required=False)
        parser.add_argument('status', type=str, required=False)
        parser.add_argument('is_archived', type=bool, required=False)
        parser.add_argument('is_recycle', type=bool, required=False)
        parser.add_argument('is_share', type=bool, required=False)
        parser.add_argument('share_password', type=str, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        data['update_time'] = datetime.now()
        try:
            note = Note.getNoteById(note_id)
            if not note:
                return {'code': 404, 'message': '笔记不存在'}, 404
            else:
                if data['type']: note.type = data['type']
                if data['title']: note.title = data['title']
                if data['content']: note.content = data['content']
                if data['folder']: note.folder = data['folder']
                if data['status']: note.status = data['status']
                if data['is_archived'] is not None: note.is_archived = data['is_archived']
                if data['is_recycle'] is not None: note.is_recycle = data['is_recycle']
                if data['is_share'] is not None: note.is_share = data['is_share']
                if data['share_password']: note.share_password = hash_password(data['share_password'])
                note.updateNote()
                return {'code': 200, 'message': '更新成功', 'data': note}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @note_ns.doc(description='删除笔记')
    @note_ns.marshal_with(note_response_model)
    def delete(self, note_id):
        try:
            note = Note.getNoteById(note_id)
            if not note:
                return {'code': 404, 'message': '笔记不存在'}, 404
            else:
                # note.deleteNote()
                note.is_recycle = True
                note.updateNote()
                return {'code': 200, 'message': '删除成功'}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

class ProjectNoteManager(Resource):
    @jwt_required()
    @note_ns.doc(description='获取项目下的笔记列表')
    @note_ns.marshal_with(note_response_list_model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=False, location='args')  # query 参数
        parser.add_argument('isRecent', type=bool, required=False, location='args')
        parser.add_argument('projectId', type=str, required=False, location='args')
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        project_id = data['projectId'] if data['projectId'] else request.headers.get('X-Project-Id')
        if not project_id:
            return {'code': 400, 'message': '项目ID不能为空'}, 400
        else:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404

        try:
            # notes = Note.getNotesByProjectId(project_id)
            # 添加过滤回收站笔记的条件
            notes = Note.getNotesByProjectIdExcludeRecycled(project_id, data['title'], data['isRecent'])
            return {'code': 200, 'message': '查询成功', 'data': notes}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @note_ns.doc(description='获取项目下的笔记列表（分页）')
    @note_ns.expect(note_page_request_model)
    @note_ns.marshal_with(note_page_response_model)
    def post(self):
        project_id = request.headers.get('X-Project-Id')
        if not project_id:
            return {'code': 400, 'message': '项目ID不能为空'}, 400
        else:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=dict, required=False)
        parser.add_argument('page_no', type=int, required=False)
        parser.add_argument('page_size', type=int, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        try:
            pageData = Note.getNotesByProjectIdWithPagination(project_id, data['query'], data['page_no'], data['page_size'])
            pageData['page_no'] = data['page_no']
            pageData['page_size'] = data['page_size']
            return {'code': 200, 'message': '查询成功', 'page_data': pageData}, 200
        except Exception as e:
            return {'code': 500, 'message': '分页查询失败：' + str(e)}, 500

class AllNoteManager(Resource):
    @jwt_required()
    @note_ns.doc(description='获取所有笔记列表')
    @note_ns.marshal_with(note_response_list_model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('isRecent', type=str, required=False)
        query_args = parser.parse_args()

        try:
            current_user_id = get_jwt_identity()
            # notes = Note.getNotesByUserId(current_user_id)

            # 添加过滤回收站笔记的条件
            notes = Note.getNotesByUserIdExcludeRecycled(current_user_id)
            if query_args['isRecent']:
                notes = [note for note in notes if note.updated_at > datetime.now() - timedelta(days=30)]
            return {'code': 200, 'message': '查询成功', 'data': notes}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500