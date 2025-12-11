# tests/test_auth_dependencies.py
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from backend.User.utils.security import create_access_token
from backend.User.utils import auth_dependencies
from backend.User.models.user import User


class TestGetDb:
    def test_get_db_yields_session(self):
        """Test that get_db yields a session and closes it"""
        with patch.object(auth_dependencies, 'SessionLocal') as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            
            gen = auth_dependencies.get_db()
            db = next(gen)
            
            assert db == mock_db
            
            # Finish the generator
            try:
                next(gen)
            except StopIteration:
                pass
            
            mock_db.close.assert_called_once()


class TestGetCurrentUser:
    def test_get_current_user_success(self):
        """Test successful user retrieval from token"""
        mock_db = MagicMock()
        mock_user = User(id=1, phone_number="1234567890", name="Test")
        
        # Create a valid token
        token = create_access_token({"sub": "1234567890"})
        
        with patch.object(auth_dependencies.user_crud, 'get_user_by_username', return_value=mock_user):
            result = auth_dependencies.get_current_user(token=token, db=mock_db)
            assert result == mock_user

    def test_get_current_user_invalid_token(self):
        """Test that invalid token raises 401"""
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            auth_dependencies.get_current_user(token="invalid.token.here", db=mock_db)
        
        assert exc_info.value.status_code == 401

    def test_get_current_user_no_sub_in_token(self):
        """Test that token without sub raises 401"""
        mock_db = MagicMock()
        
        # Create token without 'sub'
        token = create_access_token({"role": "user"})
        
        with pytest.raises(HTTPException) as exc_info:
            auth_dependencies.get_current_user(token=token, db=mock_db)
        
        assert exc_info.value.status_code == 401

    def test_get_current_user_user_not_found(self):
        """Test that non-existent user raises 401"""
        mock_db = MagicMock()
        
        token = create_access_token({"sub": "nonexistent"})
        
        with patch.object(auth_dependencies.user_crud, 'get_user_by_username', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                auth_dependencies.get_current_user(token=token, db=mock_db)
            
            assert exc_info.value.status_code == 401

