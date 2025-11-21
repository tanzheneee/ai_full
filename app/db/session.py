# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_db_url  # 导入配置获取函数
from typing import Generator
from sqlalchemy.orm import Session

engine = None  # 全局 Engine 实例
SessionLocal = None

def init_db_engine():
    """在应用启动后，使用 Nacos 配置初始化数据库连接引擎"""
    global engine,SessionLocal

    DB_URL = get_db_url()
    if not DB_URL:
        raise RuntimeError("Database URL not found in Nacos configuration.")

    # 创建 SQLAlchemy 引擎
    engine = create_engine(
        DB_URL,
        pool_pre_ping=True,
        pool_size=10  # 使用配置中的连接池大小
    )


    # 创建 SessionLocal 实例（用于创建数据库会话）
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


"""
    依赖注入函数：获取一个数据库会话
    Generator[Session, None, None]： 这是 Python 的类型提示，表明这个函数是一个生成器。
        它将 yield（生成）一个 Session 类型的对象给调用者（即 FastAPI 路由）。
        它不接受外部发送给生成器的值（第二个 None）。
        它在结束时没有返回值（第三个 None）。
    
    生成器: yield
    
"""
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()