from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, reqparse
from app.controllers import note_ns
from app.models import Note, Project
from .note_api_model import note_response_model, note_add_request_model, note_update_request_model, note_response_list_model, note_page_request_model, note_page_response_model
from datetime import datetime, timedelta
from app.utils import hash_password
import os
import zipfile
import re
import tempfile
from flask import send_file

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

class NoteExportManager(Resource):
    @jwt_required()
    @note_ns.doc('根据笔记 ID 列表导出笔记内容为 MarkDown 格式')
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            parser = reqparse.RequestParser()
            parser.add_argument('note_ids', type=str, required=True, help='笔记 ID 列表')
            data = parser.parse_args()

            note_ids = data['note_ids'].split(',')
            if not note_ids or not isinstance(note_ids, list):
                return {'code': 400, 'message': '笔记 ID 列表不能为空'}, 400

            # 验证用户权限并获取笔记
            notes = []
            for note_id in note_ids:
                note = Note.getNoteById(note_id)
                if not note:
                    return {'code': 404, 'message': f'笔记 {note_id} 不存在'}, 404

                # 验证笔记属于当前用户
                project = Project.getProjectById(note.project_id)
                if not project or str(project.account_id) != current_user_id:
                    return {'code': 403, 'message': f'无权限访问笔记 {note_id}'}, 403

                notes.append(note)

            # 如果只有一个笔记，直接导出为 Markdown 文件
            if len(notes) == 1:
                note = notes[0]

                # 创建Markdown格式的内容
                md_content = self._convert_to_markdown(note)

                # 使用笔记标题作为文件名，支持空格和中文，移除特殊字符
                # safe_title = self._sanitize_filename(note.title)
                safe_title = note.title
                if not safe_title:
                    safe_title = f"note_{note.id}"
                md_filename = f"{safe_title}.md"

                # 创建临时文件
                temp_dir = tempfile.mkdtemp()
                md_path = os.path.join(temp_dir, md_filename)

                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                # 返回 Markdown 文件下载
                return send_file(
                    md_path,
                    as_attachment=True,
                    download_name=md_filename,
                    mimetype='text/markdown'
                )
            else:
                # 多个笔记则打包为 ZIP 文件
                # 创建临时文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_dir = tempfile.mkdtemp()
                zip_filename = f"notes_export_{timestamp}.zip"
                zip_path = os.path.join(temp_dir, zip_filename)

                # 创建ZIP文件
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, note in enumerate(notes):
                        # 创建Markdown格式的内容
                        md_content = self._convert_to_markdown(note)

                        # 使用笔记标题作为文件名，支持空格和中文，移除特殊字符
                        safe_title = self._sanitize_filename(note.title)
                        safe_title = note.title
                        if not safe_title:
                            safe_title = f"note_{note.id}"
                        # 防止文件名重复
                        file_name = f"{safe_title}.md"
                        if file_name in zipf.namelist():
                            file_name = f"{safe_title}_{i}.md"

                        # 将内容写入ZIP
                        zipf.writestr(file_name, md_content)

                # 返回 ZIP 文件下载
                return send_file(
                    zip_path,
                    as_attachment=True,
                    download_name=zip_filename,
                    mimetype='application/zip'
                )
        except Exception as e:
            return {'code': 500, 'message': f'导出失败：{str(e)}'}, 500

    def _sanitize_filename(self, title):
        """清理文件名，保留字母、数字、空格、中文字符和基本标点"""
        # 使用正则表达式保留字母、数字、空格、中文字符和基本标点
        # \w 包括字母、数字、下划线
        # \u4e00-\u9fff 匹配中文字符
        # \s 匹配空白字符（包括空格）
        # 允许的标点符号：- _ . ( ) [ ] 等
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff\-\_\.\(\)\[\]\,\!\?\u3001\u3002\uFF0C\uFF1A\uFF1B\uFF1F\uFF01]', '_',
                            title)

        # 替换多个连续的空格为单个空格
        safe_title = re.sub(r'\s+', ' ', safe_title)

        # 去除首尾空格
        safe_title = safe_title.strip()

        # 限制文件名长度，防止过长
        max_length = 100
        if len(safe_title) > max_length:
            safe_title = safe_title[:max_length]
        print(safe_title)
        return safe_title

    def _convert_to_markdown(self, note):
        """将笔记转换为Markdown格式"""
        # 基础Markdown格式
        md_content = ""
        # md_content = f"# {note.title}\n\n"

        # 添加元数据信息
        # md_content += f"> 创建时间: {note.created_at}\n"
        # md_content += f"> 更新时间: {note.updated_at}\n\n"

        # 添加笔记内容
        md_content += note.content

        return md_content