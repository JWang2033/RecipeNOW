# backend/User/models/pantry_item.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from backend.User.database import Base


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)
    unit = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
