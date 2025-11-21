from sqlalchemy import Column, Integer, String
from app.db.base import Base


class UserModel(Base):
    """对应数据库中的 t_user 表"""
    __tablename__ = 't_user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True)
    pwd = Column(String(255))
    mobile = Column(String(32))