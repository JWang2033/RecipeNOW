# backend/User/crud/preferences_crud.py

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.User.models.preferences import UserPreference


def get_preferences(db: Session, user_id: int) -> Optional[UserPreference]:
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    return db.scalar(stmt)


def upsert_preferences(db: Session, user_id: int, **updates: Any) -> UserPreference:
    prefs = get_preferences(db, user_id=user_id)
    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)

    for field, value in updates.items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)
    return prefs


def delete_preferences(db: Session, user_id: int) -> None:
    prefs = get_preferences(db, user_id=user_id)
    if prefs:
        db.delete(prefs)
        db.commit()
