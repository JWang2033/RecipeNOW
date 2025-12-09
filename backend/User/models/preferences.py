# backend/User/models/preferences.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from backend.User.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    diets = Column(JSON, default=list)
    allergens = Column(JSON, default=list)
    max_cooking_time = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
