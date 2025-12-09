# backend/User/routers/pantry_router.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.User.crud import pantry_crud
from backend.User.database import get_db
from backend.User.schemas.pantry_schemas import (
    PantryBulkRequest,
    PantryItemCreate,
    PantryItemOut,
    PantryItemUpdate,
)
from backend.User.utils.auth_dependencies import get_current_user

router = APIRouter(prefix="/pantry", tags=["Pantry"])


def _require_item(db: Session, user_id: int, item_id: int):
    item = pantry_crud.get_item(db, user_id=user_id, item_id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pantry item not found")
    return item


def _normalize_payload(data: dict) -> dict:
    qty = data.get("quantity")
    if qty is not None:
        data["quantity"] = str(qty)
    return data


@router.get("/", response_model=list[PantryItemOut])
def list_items(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    items = pantry_crud.list_items(db, user_id=current_user.id)
    return items


@router.post("/", response_model=PantryItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: PantryItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payload = _normalize_payload(item_in.model_dump())
    item = pantry_crud.create_item(db, user_id=current_user.id, **payload)
    return item


@router.post("/bulk", response_model=list[PantryItemOut], status_code=status.HTTP_201_CREATED)
def create_items_bulk(
    body: PantryBulkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items = [_normalize_payload(item.model_dump()) for item in body.items]
    created = pantry_crud.bulk_create_items(db, user_id=current_user.id, items=items)
    return created


@router.put("/{item_id}", response_model=PantryItemOut)
def update_item(
    item_id: int,
    updates: PantryItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = _require_item(db, current_user.id, item_id)
    update_data = _normalize_payload(updates.model_dump(exclude_unset=True))
    if not update_data:
        return item
    return pantry_crud.update_item(db, item, **update_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = _require_item(db, current_user.id, item_id)
    pantry_crud.delete_item(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_items(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pantry_crud.clear_items(db, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
