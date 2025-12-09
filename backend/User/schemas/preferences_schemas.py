# backend/User/schemas/preferences_schemas.py

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class UserPreferencesResponse(BaseModel):
    diets: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    max_cooking_time: Optional[int] = None
    difficulty: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    diets: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    max_cooking_time: Optional[int] = Field(default=None)
    difficulty: Optional[Literal['easy', 'medium', 'hard']] = None

