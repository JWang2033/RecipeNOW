# backend/User/crud/user_crud.py

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.User.models.user import User
from backend.User.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
)


# ---------- 查询类函数 ----------

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据用户 ID 查询用户。
    """
    return db.get(User, user_id)


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """
    根据手机号查询用户（唯一）。
    """
    stmt = select(User).where(User.phone_number == phone_number)
    return db.scalar(stmt)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    为兼容旧代码（auth_dependencies 里用 username）：
    这里把 username 当作 phone_number 使用。
    """
    return get_user_by_phone(db, phone_number=username)


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    分页列出用户。
    """
    stmt = select(User).offset(skip).limit(limit)
    return list(db.scalars(stmt))


# ---------- 创建用户（使用已 hash 的密码）----------

def create_user_with_hashed_password(
    db: Session,
    user_in: UserCreate,
    hashed_password: str,
) -> User:
    """
    注册时使用：传入已经 hash 好的密码。
    业务规则：
    - phone_number 不可重复：如果已存在则抛 ValueError，由 router 转成 400/409。
    """

    existing = get_user_by_phone(db, user_in.phone_number)
    if existing:
        raise ValueError("Phone number already registered")

    user = User(
        name=user_in.name,
        hashed_password=hashed_password,
        phone_number=user_in.phone_number,
        preference=user_in.preference,
        allergen=user_in.allergen,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- 如果你想要一个方便的 create_user（不 hash），也可以保留 ----------
def create_user(db: Session, user_in: UserCreate) -> User:
    """
    简单版本：直接存明文密码（一般不建议在正式环境用）。
    这里只是为了兼容旧代码，如果不用可以删掉。
    """
    user = User(
        name=user_in.name,
        hashed_password=user_in.password,  # 注意：这里直接用 password，当作 hashed_password 存
        phone_number=user_in.phone_number,
        preference=user_in.preference,
        allergen=user_in.allergen,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- 更新用户 ----------

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """
    更新用户信息（部分字段）。
    - 如果要修改 phone_number，需要检查唯一性。
    - 密码修改同样走这里（传入的是已经 hash 好的密码会更安全）。
    """

    update_data = user_in.model_dump(exclude_unset=True)

    # 如果要改手机号，先做唯一性检查
    if "phone_number" in update_data:
        new_phone = update_data["phone_number"]
        existing = get_user_by_phone(db, new_phone)
        if existing and existing.id != user.id:
            raise ValueError("Phone number already registered by another user")

    for field, value in update_data.items():
        if field == "password":
            # 如果你在上层已经 hash 了，可以映射到 hashed_password
            user.hashed_password = value
        else:
            setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- 删除用户 ----------

def delete_user(db: Session, user: User) -> None:
    """
    删除用户。
    """
    db.delete(user)
    db.commit()
