from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from backend.User.schemas import user_schemas
from backend.User.crud import user_crud
from backend.User.utils.security import verify_password, create_access_token
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
# ✅ User Login
# -------------------------
@router.post("/login/user")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username, "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# ✅ Register New User
# -------------------------
@router.post("/register/user", response_model=user_schemas.UserOut)
def register_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db),
):
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    created_user = user_crud.create_user(db=db, user=user)
    return created_user
