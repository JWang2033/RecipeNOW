# tests/test_preferences_crud.py
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from backend.User.crud import preferences_crud
from backend.User.models.preferences import UserPreference


class TestPreferencesCrud:
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    def test_get_preferences(self, mock_db):
        pref = UserPreference(id=1, user_id=1, diets=["vegan"], allergens=["nuts"])
        mock_db.scalar.return_value = pref
        
        result = preferences_crud.get_preferences(mock_db, user_id=1)
        assert result == pref

    def test_get_preferences_not_found(self, mock_db):
        mock_db.scalar.return_value = None
        result = preferences_crud.get_preferences(mock_db, user_id=999)
        assert result is None

    def test_upsert_preferences_create_new(self, mock_db):
        mock_db.scalar.return_value = None  # No existing preferences
        
        result = preferences_crud.upsert_preferences(
            mock_db, user_id=1, diets=["vegetarian"], allergens=["nuts"]
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_upsert_preferences_update_existing(self, mock_db):
        existing_pref = UserPreference(id=1, user_id=1, diets=["vegan"])
        mock_db.scalar.return_value = existing_pref
        
        result = preferences_crud.upsert_preferences(
            mock_db, user_id=1, diets=["vegetarian"]
        )
        
        assert existing_pref.diets == ["vegetarian"]
        mock_db.add.assert_not_called()  # Shouldn't add since it exists
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_delete_preferences_exists(self, mock_db):
        pref = UserPreference(id=1, user_id=1)
        mock_db.scalar.return_value = pref
        
        preferences_crud.delete_preferences(mock_db, user_id=1)
        
        mock_db.delete.assert_called_once_with(pref)
        mock_db.commit.assert_called_once()

    def test_delete_preferences_not_exists(self, mock_db):
        mock_db.scalar.return_value = None
        
        preferences_crud.delete_preferences(mock_db, user_id=999)
        
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

