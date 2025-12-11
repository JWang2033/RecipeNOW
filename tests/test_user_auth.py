# tests/test_user_auth.py
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.User.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    _normalize_password,
)
from backend.User.crud import user_crud, pantry_crud
from backend.User.models.user import User
from backend.User.models.pantry_item import PantryItem
from backend.User.schemas.user_schemas import UserCreate, UserUpdate


# ==================== Security Utils Tests ====================

class TestPasswordHashing:
    def test_get_password_hash_returns_string(self):
        hashed = get_password_hash("mypassword123")
        assert isinstance(hashed, str)
        assert hashed.startswith("$2")  # bcrypt prefix

    def test_verify_password_correct(self):
        password = "testpassword"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_invalid_hash(self):
        assert verify_password("password", "invalid-hash") is False

    def test_normalize_password_truncates_long_password(self):
        long_password = "a" * 100
        normalized = _normalize_password(long_password)
        assert len(normalized) == 72

    def test_normalize_password_handles_none(self):
        normalized = _normalize_password(None)
        assert normalized == b""

    def test_normalize_password_short(self):
        short = "abc"
        normalized = _normalize_password(short)
        assert normalized == b"abc"


class TestJWT:
    def test_create_access_token(self):
        token = create_access_token({"sub": "1234567890", "role": "user"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        token = create_access_token({"sub": "testuser"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"

    def test_decode_access_token_invalid(self):
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_create_access_token_with_custom_expiry(self):
        token = create_access_token(
            {"sub": "user"},
            expires_delta=timedelta(minutes=5)
        )
        assert isinstance(token, str)

    def test_decode_token_contains_exp(self):
        token = create_access_token({"sub": "user123"})
        payload = decode_access_token(token)
        assert "exp" in payload


# ==================== User CRUD Tests ====================

class TestUserCrud:
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    def test_get_user_by_id(self, mock_db):
        mock_user = User(id=1, name="Test", phone_number="123")
        mock_db.get.return_value = mock_user
        
        result = user_crud.get_user_by_id(mock_db, 1)
        assert result == mock_user
        mock_db.get.assert_called_once_with(User, 1)

    def test_get_user_by_id_not_found(self, mock_db):
        mock_db.get.return_value = None
        result = user_crud.get_user_by_id(mock_db, 999)
        assert result is None

    def test_get_user_by_phone(self, mock_db):
        mock_user = User(id=1, phone_number="1234567890")
        mock_db.scalar.return_value = mock_user
        
        result = user_crud.get_user_by_phone(mock_db, "1234567890")
        assert result == mock_user

    def test_get_user_by_phone_not_found(self, mock_db):
        mock_db.scalar.return_value = None
        result = user_crud.get_user_by_phone(mock_db, "nonexistent")
        assert result is None

    def test_get_user_by_username_delegates_to_phone(self, mock_db):
        mock_user = User(id=1, phone_number="123")
        mock_db.scalar.return_value = mock_user
        
        result = user_crud.get_user_by_username(mock_db, "123")
        assert result == mock_user

    def test_list_users(self, mock_db):
        mock_users = [User(id=1), User(id=2)]
        mock_db.scalars.return_value = iter(mock_users)
        
        result = user_crud.list_users(mock_db, skip=0, limit=10)
        assert len(result) == 2

    def test_list_users_empty(self, mock_db):
        mock_db.scalars.return_value = iter([])
        result = user_crud.list_users(mock_db)
        assert len(result) == 0

    def test_create_user_with_hashed_password_success(self, mock_db):
        mock_db.scalar.return_value = None  # No existing user
        
        user_in = UserCreate(
            name="Test User",
            phone_number="1234567890",
            password="testpass123",
            preference="vegetarian",
            allergen="nuts"
        )
        
        user_crud.create_user_with_hashed_password(mock_db, user_in, "hashed_password")
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_user_duplicate_phone_raises(self, mock_db):
        existing_user = User(id=1, phone_number="1234567890")
        mock_db.scalar.return_value = existing_user
        
        user_in = UserCreate(
            name="Test",
            phone_number="1234567890",
            password="testpass123"
        )
        
        with pytest.raises(ValueError, match="Phone number already registered"):
            user_crud.create_user_with_hashed_password(mock_db, user_in, "hash")

    def test_create_user_simple(self, mock_db):
        user_in = UserCreate(
            name="Simple User",
            phone_number="9999999999",
            password="plainpass"
        )
        
        user_crud.create_user(mock_db, user_in)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_update_user_name(self, mock_db):
        user = User(id=1, name="Old Name", phone_number="123")
        mock_db.scalar.return_value = None
        
        user_in = UserUpdate(name="New Name")
        user_crud.update_user(mock_db, user, user_in)
        
        assert user.name == "New Name"
        mock_db.commit.assert_called()

    def test_update_user_password(self, mock_db):
        user = User(id=1, name="User", phone_number="123", hashed_password="old")
        mock_db.scalar.return_value = None
        
        user_in = UserUpdate(password="newhashed")
        user_crud.update_user(mock_db, user, user_in)
        
        assert user.hashed_password == "newhashed"

    def test_update_user_phone_conflict(self, mock_db):
        user = User(id=1, phone_number="111")
        other_user = User(id=2, phone_number="222")
        mock_db.scalar.return_value = other_user
        
        user_in = UserUpdate(phone_number="222")
        
        with pytest.raises(ValueError, match="already registered"):
            user_crud.update_user(mock_db, user, user_in)

    def test_update_user_phone_same_user_ok(self, mock_db):
        user = User(id=1, phone_number="111")
        mock_db.scalar.return_value = user  # Same user
        
        user_in = UserUpdate(phone_number="111")
        user_crud.update_user(mock_db, user, user_in)
        mock_db.commit.assert_called()

    def test_delete_user(self, mock_db):
        user = User(id=1)
        user_crud.delete_user(mock_db, user)
        
        mock_db.delete.assert_called_once_with(user)
        mock_db.commit.assert_called_once()


# ==================== Pantry CRUD Tests ====================

class TestPantryCrud:
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    def test_list_items(self, mock_db):
        items = [PantryItem(id=1, user_id=1), PantryItem(id=2, user_id=1)]
        mock_db.scalars.return_value = iter(items)
        
        result = pantry_crud.list_items(mock_db, user_id=1)
        assert len(result) == 2

    def test_list_items_empty(self, mock_db):
        mock_db.scalars.return_value = iter([])
        result = pantry_crud.list_items(mock_db, user_id=1)
        assert len(result) == 0

    def test_get_item(self, mock_db):
        item = PantryItem(id=1, user_id=1, name="Egg")
        mock_db.scalar.return_value = item
        
        result = pantry_crud.get_item(mock_db, user_id=1, item_id=1)
        assert result == item

    def test_get_item_not_found(self, mock_db):
        mock_db.scalar.return_value = None
        result = pantry_crud.get_item(mock_db, user_id=1, item_id=999)
        assert result is None

    def test_create_item(self, mock_db):
        pantry_crud.create_item(mock_db, user_id=1, name="Milk", quantity=2)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_bulk_create_items(self, mock_db):
        items_data = [
            {"name": "Egg", "quantity": 6},
            {"name": "Milk", "quantity": 1}
        ]
        
        pantry_crud.bulk_create_items(mock_db, user_id=1, items=items_data)
        mock_db.add_all.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_bulk_create_items_empty(self, mock_db):
        result = pantry_crud.bulk_create_items(mock_db, user_id=1, items=[])
        assert result == []
        mock_db.add_all.assert_not_called()

    def test_update_item(self, mock_db):
        item = PantryItem(id=1, name="Old", quantity=1)
        
        pantry_crud.update_item(mock_db, item, name="New", quantity=5)
        
        assert item.name == "New"
        assert item.quantity == 5
        mock_db.commit.assert_called_once()

    def test_delete_item(self, mock_db):
        item = PantryItem(id=1)
        pantry_crud.delete_item(mock_db, item)
        
        mock_db.delete.assert_called_once_with(item)
        mock_db.commit.assert_called_once()

    def test_clear_items(self, mock_db):
        items = [PantryItem(id=1), PantryItem(id=2)]
        mock_db.scalars.return_value = iter(items)
        
        pantry_crud.clear_items(mock_db, user_id=1)
        
        assert mock_db.delete.call_count == 2
        mock_db.commit.assert_called_once()

    def test_clear_items_none(self, mock_db):
        mock_db.scalars.return_value = iter([])
        pantry_crud.clear_items(mock_db, user_id=1)
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_called_once()