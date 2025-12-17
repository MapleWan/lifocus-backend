from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='笔记ID')
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id'), nullable=False, comment='项目ID')
    type = db.Column(db.String(64), nullable=False, comment='笔记类型')
    title = db.Column(db.String(255), nullable=False, comment='笔记标题')
    content = db.Column(db.Text(), nullable=False, comment='笔记内容')
    folder = db.Column(db.String(255), default='default', comment='笔记存储文件夹')
    status = db.Column(db.String(64), default='active', comment='笔记状态')
    is_archived = db.Column(db.Boolean(), default=False, comment='笔记是否归档')
    is_recycle = db.Column(db.Boolean(), default=False, comment='笔记是否回收站')
    is_share = db.Column(db.Boolean(), default=False, comment='笔记是否分享')
    share_password = db.Column(db.String(255), default='', comment='笔记分享密码')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 添加笔记
    def addNote(self):
        db.session.add(self)
        db.session.commit()

    # 更新笔记
    def updateNote(self):
        db.session.add(self)
        db.session.commit()

    # 删除笔记
    def deleteNote(self):
        db.session.delete(self)
        db.session.commit()

    # 打印笔记信息
    def dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'folder': self.folder,
            'status': self.status,
            'is_archived': self.is_archived,
            'is_recycle': self.is_recycle,
            'is_share': self.is_share,
            'share_password': self.share_password,
            'created_at': format_datetime_to_string(self.created_at),
            'updated_at': format_datetime_to_string(self.updated_at)
        }

    # 根据笔记ID获取笔记信息
    @staticmethod
    def getNoteById(note_id):
        return Note.query.filter_by(id=note_id).first()

    # 查询项目下的所有笔记
    @staticmethod
    def getNotesByProjectId(project_id):
        return Note.query.filter_by(project_id=project_id).all()

    # 获取项目下的笔记（分页）
    @staticmethod
    def getNotesByProjectIdWithPagination(project_id, query_condition, page_no, page_size):
        query = Note.query.filter_by(project_id=project_id)
        if query_condition:
            allowed_query_condition_keys = ['type', 'title', 'folder', 'status', 'is_archived', 'is_recycle', 'is_share', 'created_start_time', 'created_end_time', 'updated_start_time', 'updated_end_time']
            for key, value in query_condition.items():
                if key not in allowed_query_condition_keys:
                    continue
                if key in ['title', 'folder']:
                    query = query.filter(getattr(Note, key).like('%{}%'.format(value)))
                elif key in ['created_start_time', 'updated_start_time']:
                    query = query.filter(Note.created_at >= value) if key == 'created_start_time' else query.filter(Note.updated_at >= value)
                elif key in ['created_end_time', 'updated_end_time']:
                    query = query.filter(Note.created_at <= value) if key == 'created_start_time' else query.filter(Note.updated_at <= value)
                else:
                    query = query.filter(getattr(Note, key) == value)
        total = query.count()
        notes = query.offset((page_no - 1) * page_size).limit(page_size).all()
        return {
            'data': notes,
            'total': total,
            'pages': (total + page_size - 1) // page_size
        }