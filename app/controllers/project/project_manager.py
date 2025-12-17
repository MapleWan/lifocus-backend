from flask_jwt_extended import jwt_required
from flask_restx import Resource, reqparse
from app.controllers import project_ns
from app.models import Project
from .project_api_model import project_response_list_model, project_delete_response_model, project_add_request_model, project_response_model, project_update_request_model
from datetime import datetime
from flask_jwt_extended import get_jwt_identity

class SingleProjectManager(Resource):
    @jwt_required()
    @project_ns.doc(description='根据项目 id 获取项目信息')
    @project_ns.marshal_with(project_response_model)
    def get(self, project_id):
        try:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404
            return {'code': 200, 'message': '查询成功', 'data': project}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @project_ns.doc(description='新增项目')
    @project_ns.expect(project_add_request_model)
    @project_ns.marshal_with(project_response_model)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('icon', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        current_user_id = get_jwt_identity()
        if Project.getProjectByName(data['name'], current_user_id):
            return {'code': 400, 'message': '项目<{}>已存在'.format(data['name'])}, 400
        try:
            data.account_id = get_jwt_identity()
            project = Project(**data)
            project.addProject()
            return {'code': 201, 'message': '新增成功', 'data': project}, 201
        except Exception as e:
            return {'code': 500, 'message': '新增失败，' + str(e)}, 500

    @jwt_required()
    @project_ns.doc(description='更新项目信息')
    @project_ns.expect(project_update_request_model)
    @project_ns.marshal_with(project_response_model)
    def put(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=False)
        parser.add_argument('name', type=str, required=False)
        parser.add_argument('icon', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('folder', type=str, required=False)
        parser.add_argument('status', type=str, required=False)
        parser.add_argument('is_archived', type=bool, required=False)
        parser.add_argument('is_recycle', type=bool, required=False)
        parser.add_argument('is_favor', type=bool, required=False)
        try:
            data = parser.parse_args()
        except Exception as e:
            return {'code': 400, 'message': '参数错误'}, 400
        data['update_time'] = datetime.now()
        try:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404
            else:
                if data['type']: project.type = data['type']
                if data['name']: project.name = data['name']
                if data['icon']: project.icon = data['icon']
                if data['description']: project.description = data['description']
                if data['folder']: project.folder = data['folder']
                if data['status']: project.status = data['status']
                if 'is_archived' in data and data['is_archived'] is not None:
                    project.is_archived = data['is_archived']
                if 'is_recycle' in data and data['is_recycle'] is not None:
                    project.is_recycle = data['is_recycle']
                if 'is_favor' in data and data['is_favor'] is not None:
                    project.is_favor = data['is_favor']
                project.updateProject()
                return {'code': 200, 'message': '更新成功', 'data': project}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

    @jwt_required()
    @project_ns.doc(description='删除项目')
    @project_ns.marshal_with(project_delete_response_model)
    def delete(self, project_id):
        try:
            project = Project.getProjectById(project_id)
            if not project:
                return {'code': 404, 'message': '项目不存在'}, 404
            else:
                project.deleteProject()
                return {'code': 200, 'message': '删除成功'}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

class UserProjectManager(Resource):
    # @jwt_required()
    # @project_ns.doc(description='获取用户项目列表')
    # @project_ns.marshal_with(project_response_list_model)
    # def get(self, user_id):
    #     try:
    #         projects = Project.getProjectsByAccountId(user_id)
    #         return {'code': 200, 'message': '查询成功', 'data': projects}, 200
    #     except Exception as e:
    #         return {'code': 500, 'message': str(e)}, 500
    @jwt_required()
    @project_ns.doc(description='获取用户项目列表')
    @project_ns.marshal_with(project_response_list_model)
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            projects = Project.getProjectsByAccountId(current_user_id)
            return {'code': 200, 'message': '查询成功', 'data': projects}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500