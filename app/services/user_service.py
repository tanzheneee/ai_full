from sqlalchemy.orm import Session
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate, UserUpdate
from app.utils.crypt_utils import hash_password, verify_password
from app.utils.db_session_utils import crud_commit
import logging

logger = logging.getLogger(__name__)


# --- CRUD 操作 ---

# Read (查询单个用户)
def get_user(db: Session, user_id: int) -> UserModel | None:
    userModel = db.query(UserModel).filter(UserModel.id == user_id).first()
    logger.info("get user info id: %s, res: %s", user_id, userModel
                , extra={
            "action": "get_user"
        })
    return userModel


# Read (查询多个用户)
def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()


# Create (创建用户)
def create_user(db: Session, user: UserCreate) -> UserModel:
    hashed_pwd = hash_password(user.pwd)

    db_user = UserModel(name=user.name, pwd=hashed_pwd, mobile=user.mobile)
    db.add(db_user)

    return crud_commit(db, db_user)


# Update (更新用户)
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> UserModel | None:
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        return None

    # 遍历更新模型中的非空字段
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "pwd" and value is not None:
            # 💡 如果更新了密码，也需要进行 Bcrypt 哈希
            setattr(db_user, key, hash_password(value))
        else:
            setattr(db_user, key, value)

    return crud_commit(db, db_user)


# Delete (删除用户)
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db.delete(db_user)
        crud_commit(db, None)
        return True
    return False


# Read (验证用户，用于登录)
def authenticate_user(db: Session, name: str, password: str) -> UserModel | None:
    """验证用户名和密码"""

    db_user = db.query(UserModel).filter(UserModel.name == name).first()
    if not db_user:
        return None

    # 💡 关键修改：使用 verify_password 进行验证
    if verify_password(password, db_user.pwd):
        return db_user

    return None
