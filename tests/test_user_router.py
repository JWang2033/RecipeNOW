# tests/test_user_router.py
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from backend.User.utils.security import get_password_hash
from backend.User.models.user import User


class TestUserRouterLogin:
    def test_login_success(self, client: TestClient, monkeypatch):
        """Test successful login"""
        from backend.User.routers import user_router
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.phone_number = "1234567890"
        mock_user.hashed_password = get_password_hash("password123")
        mock_user.name = "Test User"
        
        def mock_get_db():
            mock_db = MagicMock()
            yield mock_db
        
        monkeypatch.setattr(user_router, "get_db", mock_get_db)
        monkeypatch.setattr(
            "backend.User.crud.user_crud.get_user_by_phone",
            lambda db, phone_number: mock_user
        )
        
        resp = client.post(
            "/auth/login",
            data={"username": "1234567890", "password": "password123"}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, monkeypatch):
        """Test login with wrong password"""
        from backend.User.routers import user_router
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.phone_number = "1234567890"
        mock_user.hashed_password = get_password_hash("correctpassword")
        
        def mock_get_db():
            mock_db = MagicMock()
            yield mock_db
        
        monkeypatch.setattr(user_router, "get_db", mock_get_db)
        monkeypatch.setattr(
            "backend.User.crud.user_crud.get_user_by_phone",
            lambda db, phone_number: mock_user
        )
        
        resp = client.post(
            "/auth/login",
            data={"username": "1234567890", "password": "wrongpassword"}
        )
        
        assert resp.status_code == 401

    def test_login_user_not_found(self, client: TestClient, monkeypatch):
        """Test login with non-existent user"""
        from backend.User.routers import user_router
        
        def mock_get_db():
            mock_db = MagicMock()
            yield mock_db
        
        monkeypatch.setattr(user_router, "get_db", mock_get_db)
        monkeypatch.setattr(
            "backend.User.crud.user_crud.get_user_by_phone",
            lambda db, phone_number: None
        )
        
        resp = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "password123"}
        )
        
        assert resp.status_code == 401


class TestUserRouterRegister:
    def test_register_success(self, client: TestClient, monkeypatch):
        """Test successful registration"""
        from backend.User.routers import user_router
        
        mock_created_user = MagicMock()
        mock_created_user.id = 1
        mock_created_user.phone_number = "1234567890"
        mock_created_user.name = "New User"
        mock_created_user.preference = None
        mock_created_user.allergen = None
        
        def mock_get_db():
            mock_db = MagicMock()
            yield mock_db
        
        monkeypatch.setattr(user_router, "get_db", mock_get_db)
        monkeypatch.setattr(
            "backend.User.crud.user_crud.get_user_by_phone",
            lambda db, phone_number: None  # No existing user
        )
        monkeypatch.setattr(
            "backend.User.crud.user_crud.create_user_with_hashed_password",
            lambda db, user, hashed: mock_created_user
        )
        
        resp = client.post(
            "/auth/register",
            json={
                "name": "New User",
                "phone_number": "1234567890",
                "password": "password123"
            }
        )
        
        assert resp.status_code == 200

    def test_register_duplicate_phone(self, client: TestClient, monkeypatch):
        """Test registration with existing phone number"""
        from backend.User.routers import user_router
        
        existing_user = MagicMock()
        existing_user.id = 1
        existing_user.phone_number = "1234567890"
        
        def mock_get_db():
            mock_db = MagicMock()
            yield mock_db
        
        monkeypatch.setattr(user_router, "get_db", mock_get_db)
        monkeypatch.setattr(
            "backend.User.crud.user_crud.get_user_by_phone",
            lambda db, phone_number: existing_user
        )
        
        resp = client.post(
            "/auth/register",
            json={
                "name": "New User",
                "phone_number": "1234567890",
                "password": "password123"
            }
        )
        
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

