from pydantic import BaseModel, Field


# 基础模型：用于定义公共字段
class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    mobile: str | None = Field(None, max_length=32)


# 创建模型：新增用户时需要密码
class UserCreate(UserBase):
    pwd: str = Field(..., max_length=255)


# 读取模型：用于 API 响应，不暴露密码
class UserRead(UserBase):
    id: int

    class Config:
        # 允许 ORM 对象转换为 Pydantic
        from_attributes = True

    # 更新模型：部分字段可选


class UserUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    pwd: str | None = Field(None, max_length=255)
    mobile: str | None = Field(None, max_length=32)