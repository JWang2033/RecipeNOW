# backend/User/routers/preferences_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.User.crud import preferences_crud
from backend.User.database import get_db
from backend.User.schemas.preferences_schemas import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
)
from backend.User.utils.auth_dependencies import get_current_user

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


def _to_response(pref) -> UserPreferencesResponse:
    return UserPreferencesResponse(
        diets=pref.diets or [],
        allergens=pref.allergens or [],
        max_cooking_time=pref.max_cooking_time,
        difficulty=pref.difficulty,
    )


@router.get("/", response_model=UserPreferencesResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prefs = preferences_crud.get_preferences(db, current_user.id)
    if not prefs:
        prefs = preferences_crud.upsert_preferences(db, user_id=current_user.id)
    return _to_response(prefs)


@router.put("/", response_model=UserPreferencesResponse)
def update_preferences(
    updates: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payload = updates.model_dump(exclude_unset=True)
    prefs = preferences_crud.upsert_preferences(db, user_id=current_user.id, **payload)
    return _to_response(prefs)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    preferences_crud.delete_preferences(db, user_id=current_user.id)
    return None
