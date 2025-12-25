from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, reqparse
from app.controllers import note_ns
from app.models import Note, Project
from datetime import datetime
import os
import zipfile
from werkzeug.utils import secure_filename


class NoteImportManager(Resource):
    @jwt_required()
    @note_ns.doc(description='导入笔记 - 支持单个MD文件或ZIP压缩包')
    def post(self):
        project_id = request.headers.get('X-Project-Id')
        if not project_id:
            return {'code': 400, 'message': '项目ID不能为空'}, 400

        project = Project.getProjectById(project_id)
        if not project:
            return {'code': 404, 'message': '项目不存在'}, 404

        # 检查是否有文件上传
        if 'file' not in request.files:
            return {'code': 400, 'message': '没有上传文件'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'code': 400, 'message': '没有选择文件'}, 400

        if not file:
            return {'code': 400, 'message': '文件上传失败'}, 400

        try:
            # filename = secure_filename(file.filename)
            filename = file.filename
            # 根据文件扩展名判断处理方式
            if filename.lower().endswith('.md'):
                # 单个MD文件处理
                result = self._import_single_md(file, project_id)
            elif filename.lower().endswith('.zip'):
                # ZIP压缩包处理
                result = self._import_zip_file(file, project_id)
            else:
                return {'code': 400, 'message': '只支持 .md 或 .zip 文件'}, 400

            return result
        except Exception as e:
            return {'code': 500, 'message': f'导入失败：{str(e)}'}, 500

    def _import_single_md(self, file, project_id):
        """导入单个MD文件"""
        try:
            content = file.read().decode('utf-8')

            # 生成标题（使用文件名，去除扩展名）
            filename = os.path.splitext(file.filename)[0]
            title = filename if filename else f"未命名笔记_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 创建笔记
            note_data = {
                'project_id': project_id,
                'type': 'note',
                'title': title,
                'content': content,
                'folder': 'imported',
                'status': 'active',
                'is_archived': False,
                'is_recycle': False,
                'is_share': False
            }

            note = Note(**note_data)
            note.addNote()

            return {
                'code': 200,
                'message': '单个笔记导入成功',
                'data': {'id': note.id, 'title': note.title}
            }
        except UnicodeDecodeError:
            return {'code': 500, 'message': '文件编码错误，请确保文件为UTF-8编码'}, 500

    def _import_zip_file(self, file, project_id):
        """导入ZIP压缩包中的MD文件（递归处理子文件夹）"""
        import tempfile
        import os
        import chardet

        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 保存上传的ZIP文件
                zip_path = os.path.join(temp_dir, 'upload.zip')
                file.save(zip_path)

                # 解压文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # 修复文件名编码问题
                    for info in zip_ref.infolist():
                        # 获取原始文件名
                        original_filename = info.filename

                        # 尝试修复中文文件名编码问题
                        try:
                            # 检查文件名是否包含非ASCII字符
                            original_filename.encode('ascii')
                            safe_filename = original_filename
                        except UnicodeEncodeError:
                            # 尝试使用 GBK 解码（常见于 Windows 创建的 ZIP）
                            try:
                                safe_filename = original_filename.encode('cp437').decode('gbk')
                            except (UnicodeDecodeError, UnicodeEncodeError):
                                # 如果 GBK 也不行，尝试 UTF-8
                                try:
                                    safe_filename = original_filename.encode('cp437').decode('utf-8')
                                except (UnicodeDecodeError, UnicodeEncodeError):
                                    # 最后尝试忽略错误
                                    safe_filename = original_filename.encode('utf-8', errors='ignore').decode('utf-8')

                        # 确保路径安全
                        safe_filename = os.path.normpath(safe_filename)

                        # 防止路径遍历攻击
                        if '..' in safe_filename or safe_filename.startswith('/'):
                            continue

                        # 提取文件
                        zip_ref.extract(info, temp_dir)

                        # 重命名文件（如果需要）
                        original_extracted_path = os.path.join(temp_dir, info.filename)
                        safe_extracted_path = os.path.join(temp_dir, safe_filename)

                        if os.path.exists(original_extracted_path) and original_extracted_path != safe_extracted_path:
                            try:
                                os.renames(original_extracted_path, safe_extracted_path)
                            except OSError:
                                # 如果重命名失败，继续使用原始路径
                                pass

                # 递归遍历目录，查找所有MD文件
                imported_notes = []

                # 遍历临时目录中的所有文件和子目录
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        if filename.lower().endswith('.md'):
                            file_path = os.path.join(root, filename)

                            # 读取MD文件内容
                            with open(file_path, 'r', encoding='utf-8') as md_file:
                                content = md_file.read()

                            # 生成标题（使用文件名，去除扩展名）
                            title = os.path.splitext(filename)[0]
                            # 创建笔记
                            note_data = {
                                'project_id': project_id,
                                'type': 'note',
                                'title': title,
                                'content': content,
                                'folder': 'imported',
                                'status': 'active',
                                'is_archived': False,
                                'is_recycle': False,
                                'is_share': False
                            }

                            note = Note(**note_data)
                            note.addNote()
                            imported_notes.append({'id': note.id, 'title': note.title})

                return {
                    'code': 200,
                    'message': f'成功导入 {len(imported_notes)} 个笔记',
                    'data': imported_notes
                }
        except zipfile.BadZipFile:
            return {'code': 500, 'message': 'ZIP文件格式错误'}, 500
        except UnicodeDecodeError:
            return {'code': 500, 'message': 'MD文件编码错误，请确保文件为UTF-8编码'}, 500
        except Exception as e:
            return {'code': 500, 'message': f'ZIP处理失败：{str(e)}'}, 500

