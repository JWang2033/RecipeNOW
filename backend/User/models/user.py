# backend/models/user.py
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime
from sqlalchemy.sql import func
from backend.User.database import Base  # 你的 Base 可能在 app.database 里，按你的路径改
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_reminder_on = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # user.py
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
