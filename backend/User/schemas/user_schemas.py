# backend/User/schemas/user_schemas.py

from pydantic import BaseModel, constr
from typing import Optional, List


# ------- 公共字段（不含密码） -------
class UserBase(BaseModel):
    # Name：不可空，可重复
    name: constr(strip_whitespace=True, min_length=1)

    # Phone number：不可空，不可重复（唯一约束在数据库 + CRUD）
    phone_number: constr(strip_whitespace=True, min_length=1)

    # Preference：可空，自由文本
    preference: Optional[str] = None

    # Allergen：可空，自由文本
    allergen: Optional[str] = None


# ------- 创建用户时的输入 -------
class UserCreate(UserBase):
    # Password：不可空，8 位以上（复杂度校验可在业务层做）
    password: constr(min_length=8)


# ------- 登录用的输入（如果你不用 OAuth2PasswordRequestForm，可以用这个） -------
class UserLogin(BaseModel):
    phone_number: constr(strip_whitespace=True, min_length=1)
    password: constr(min_length=8)


# ------- 更新用户信息时的输入（可选字段） -------
class UserUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    phone_number: Optional[constr(strip_whitespace=True, min_length=1)] = None
    password: Optional[constr(min_length=8)] = None
    preference: Optional[str] = None
    allergen: Optional[str] = None


# ------- 返回给前端的用户数据（不含密码） -------
class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# ------- 可选：返回用户列表时用 -------
class UserList(BaseModel):
    users: List[UserOut]
