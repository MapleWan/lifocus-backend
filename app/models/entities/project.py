from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='项目ID')
    account_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False, comment='账户ID')
    type = db.Column(db.String(64), nullable=False, comment='项目类型')
    name = db.Column(db.String(255), nullable=False, comment='项目名称')
    icon = db.Column(db.String(255), default='', comment='项目图标URL')
    description = db.Column(db.Text(), default='', comment='项目描述')
    folder = db.Column(db.Text(), default='default', comment='项目存储文件夹')
    status = db.Column(db.String(64), default='active', comment='项目状态')
    is_archived = db.Column(db.Boolean(), default=False, comment='项目是否归档')
    is_recycle = db.Column(db.Boolean(), default=False, comment='项目是否回收站')
    is_favor = db.Column(db.Boolean(), default=False, comment='项目是否收藏')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 添加项目
    def addProject(self):
        db.session.add(self)
        db.session.commit()

    # 更新项目
    def updateProject(self):
        db.session.add(self)
        db.session.commit()

    # 删除项目
    def deleteProject(self):
        db.session.delete(self)
        db.session.commit()

    # 打印项目信息
    def dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'folder': self.folder,
            'status': self.status,
            'is_archived': self.is_archived,
            'is_recycle': self.is_recycle,
            'is_favor': self.is_favor,
            'account_id': self.account_id,
            'created_at': format_datetime_to_string(self.created_at),
            'updated_at': format_datetime_to_string(self.updated_at)
        }

    # 根据项目 id 查询项目信息
    @staticmethod
    def getProjectById(id):
        return Project.query.filter_by(id=id).first()

    # 根据项目 name 查询项目信息（用于判断项目名是否重复）
    @staticmethod
    def getProjectByName(name, account_id):
        return Project.query.filter_by(name=name, account_id=account_id).first()

    # 根据关键字（名字）模糊查询项目
    @staticmethod
    def getProjectByKeyword(keyword, account_id):
        return Project.query.filter(Project.name.like('%' + keyword + '%'), Project.account_id == account_id).all()

    # 获取账户下的所有项目
    @staticmethod
    def getProjectsByAccountId(account_id):
        return Project.query.filter_by(account_id=account_id).all()

    # 获取账户下的项目（分页接口）
    '''
    根据账户ID获取项目列表（分页）
    :param account_id: 账户ID
    :param query: 查询条件 
        {
            "type": "note",
			"name": "project-3",
			"is_archived": false,
			"is_recycle": false,
			"is_favor": false,
			"created_start_time": "2025-12-17 00:00:00",
			"created_end_time": "2025-12-17 00:00:00",
			"updated_start_time": "2025-12-17 00:00:00",
			"updated_end_time: "2025-12-17 00:00:00"
		}
    :param page: 页码
    :param per_page: 每页数量
    :return: 包含项目列表、总数和总页数的字典
    '''
    @staticmethod
    def getProjectsByAccountIdWithPagination(account_id, query_conditions, page, per_page):
        query = Project.query.filter_by(account_id=account_id)

        # 处理查询条件
        if query_conditions:
            # 根据项目类型过滤
            if query_conditions.get('type'):
                query = query.filter(Project.type == query_conditions['type'])

            # 根据项目名称模糊匹配
            if query_conditions.get('name'):
                query = query.filter(Project.name.like('%' + query_conditions['name'] + '%'))

            # 根据是否归档过滤
            if query_conditions.get('is_archived') is not None:
                query = query.filter(Project.is_archived == query_conditions['is_archived'])

            # 根据是否在回收站过滤
            if query_conditions.get('is_recycle') is not None:
                query = query.filter(Project.is_recycle == query_conditions['is_recycle'])

            # 根据是否收藏过滤
            if query_conditions.get('is_favor') is not None:
                query = query.filter(Project.is_favor == query_conditions['is_favor'])

            # 根据创建时间范围过滤
            if query_conditions.get('created_start_time'):
                query = query.filter(Project.created_at >= query_conditions['created_start_time'])
            if query_conditions.get('created_end_time'):
                query = query.filter(Project.created_at <= query_conditions['created_end_time'])

            # 根据更新时间范围过滤
            if query_conditions.get('updated_start_time'):
                query = query.filter(Project.updated_at >= query_conditions['updated_start_time'])
            if query_conditions.get('updated_end_time'):
                query = query.filter(Project.updated_at <= query_conditions['updated_end_time'])
        total = query.count()
        projects = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            'data': projects,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }