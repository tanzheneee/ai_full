"""
处理orm 自动提交和刷新
"""
from sqlalchemy.orm import Session
from typing import Any, Callable, TypeVar

T = TypeVar('T') # 定义一个类型变量，用于函数返回值的类型提示

def crud_commit(db: Session, db_object: T) -> T:
    """
    统一处理数据库操作的 commit 和 refresh 流程。
    类似于 Java 中的 @Transactional 注解的轻量级实现。
    """
    try:
        db.commit()
        # 只有在对象被添加或更新后，才需要刷新。
        # 如果是 DELETE 操作，可以手动处理。
        if db_object is not None:
             db.refresh(db_object)
        return db_object
    except Exception as e:
        # 发生错误时，回滚事务
        db.rollback()
        # 可以选择重新抛出异常，或记录日志
        raise e