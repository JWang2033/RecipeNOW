# backend/schemas/user_schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional

# ✅ 用于注册/创建用户时的输入数据（来自前端）
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

# ✅ 用于返回给前端的用户数据
class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    is_reminder_on: bool

    class Config:
        orm_mode = True
