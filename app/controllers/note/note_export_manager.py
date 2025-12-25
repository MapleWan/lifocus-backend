
import os
import zipfile
import re
import tempfile
from flask import send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, reqparse
from app.controllers import note_ns
from app.models import Note, Project
from datetime import datetime

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