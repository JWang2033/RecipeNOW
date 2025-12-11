# backend/User/models/user.py

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from backend.User.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Name：不可空，可重复
    name = Column(String(100), nullable=False)

    # 存 hash 后的密码，配合 verify_password 使用
    hashed_password = Column(String(255), nullable=False)

    # Phone number：不可空，不可重复
    phone_number = Column(String(20), nullable=False, unique=True, index=True)

    # Preference：可空，自由文本
    preference = Column(Text, nullable=True)

    # Allergen：可空，自由文本
    allergen = Column(Text, nullable=True)

    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
