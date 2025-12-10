# backend/User/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from backend.User.schemas import user_schemas
from backend.User.crud import user_crud
from backend.User.utils.security import (
    verify_password,
    create_access_token,
    get_password_hash,
)
from backend.User.database import SessionLocal

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# ✅ User Login（使用手机号 + 密码）
# -------------------------
@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    phone_number = form_data.username
    user = user_crud.get_user_by_phone(db, phone_number=phone_number)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
        )

    # JWT 中的 sub 用手机号
    access_token = create_access_token(data={"sub": user.phone_number, "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------
# ✅ Register New User（用户注册）
# -------------------------
@router.post("/register", response_model=user_schemas.UserOut)
def register_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    existing = user_crud.get_user_by_phone(db, phone_number=user.phone_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    hashed_password = get_password_hash(user.password)
    created = user_crud.create_user_with_hashed_password(db, user, hashed_password)
    return created

