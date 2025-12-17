from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string
class User(db.Model):
    __tablename__ = 'user' # 表名，与数据库中的表名一致
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='账户ID')
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(128), default='', comment='用户邮箱')
    password = db.Column(db.String(255), nullable=False, comment='密码')
    salt = db.Column(db.String(32), comment='salt')
    avatar = db.Column(db.String(255), default='', comment='用户头像URL')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 添加用户
    def addUser(self):
        db.session.add(self)
        db.session.commit()
    
    # 更新用户
    def updateUser(self):
        db.session.add(self)
        db.session.commit()
    
    # 删除用户
    def deleteUser(self):
        db.session.delete(self)
        db.session.commit()
    
    # 打印用户信息
    def dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'salt': self.salt,
            'avatar': self.avatar,
            'created_at': format_datetime_to_string(self.created_at),
            'updated_at': format_datetime_to_string(self.updated_at)
        }

    # 查询用户
    @staticmethod
    def getUser(keyword):
        # return User.query.filter_by(username=keyword).first()
        return User.query.filter(
            db.or_(
                User.username == keyword,
                User.email == keyword
            )
        ).first()

    @staticmethod
    def getUserById(id):
        return User.query.filter_by(id=id).first()
    
    # 查询所有用户
    @staticmethod
    def getAllUser():
        return User.query.all()