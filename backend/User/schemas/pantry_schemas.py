# backend/User/schemas/pantry_schemas.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, constr

QuantityValue = Optional[Union[str, int, float]]


class PantryItemBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    quantity: QuantityValue = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    quantity: QuantityValue = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class PantryItemOut(PantryItemBase):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True


class PantryBulkRequest(BaseModel):
    items: List[PantryItemCreate]
