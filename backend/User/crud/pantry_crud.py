# backend/User/crud/pantry_crud.py

from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.User.models.pantry_item import PantryItem


def list_items(db: Session, user_id: int) -> List[PantryItem]:
    stmt = select(PantryItem).where(PantryItem.user_id == user_id).order_by(PantryItem.added_at.asc())
    return list(db.scalars(stmt))


def get_item(db: Session, user_id: int, item_id: int) -> Optional[PantryItem]:
    stmt = select(PantryItem).where(
        PantryItem.user_id == user_id,
        PantryItem.id == item_id,
    )
    return db.scalar(stmt)


def create_item(db: Session, user_id: int, **data) -> PantryItem:
    item = PantryItem(user_id=user_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create_items(db: Session, user_id: int, items: Iterable[dict]) -> List[PantryItem]:
    objs = [PantryItem(user_id=user_id, **data) for data in items]
    if not objs:
        return []
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_item(db: Session, item: PantryItem, **updates) -> PantryItem:
    for field, value in updates.items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: PantryItem) -> None:
    db.delete(item)
    db.commit()


def clear_items(db: Session, user_id: int) -> None:
    stmt = select(PantryItem).where(PantryItem.user_id == user_id)
    for item in db.scalars(stmt):
        db.delete(item)
    db.commit()
