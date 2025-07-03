import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock, patch
from app.crud import user as crud_user
from app.models.user import UserDB

def test_get_user_by_username():
    """Test retrieving a user by username from the database"""
    # Arrange: Mock the database session and query chain
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = "mock_user"
    
    # Act: Call the function under test
    result = crud_user.get_user_by_username(mock_db, "testuser")
    
    # Assert: Verify the result and that correct database methods were called
    assert result == "mock_user"
    mock_db.query.assert_called_once_with(UserDB)
    mock_query.filter.assert_called_once()

def test_create_user():
    """Test creating a new user with default balance values"""
    # Arrange: Mock the database session and UserDB constructor
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    username = "testuser"
    with patch("app.crud.user.UserDB") as MockUserDB:
        mock_user_instance = MagicMock()
        mock_user_instance.username = username
        mock_user_instance.balance_pen = 100.0
        mock_user_instance.balance_usd = 0.0
        MockUserDB.return_value = mock_user_instance

        # Act: Call the function under test
        result = crud_user.create_user(mock_db, username)

        # Assert: Verify database operations and returned object
        mock_db.add.assert_called_once_with(mock_user_instance)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user_instance)
        assert result == mock_user_instance

def test_update_user():
    """Test updating an existing user in the database"""
    # Arrange: Mock the database session and user object
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    user = MagicMock()
    
    # Act: Call the function under test
    result = crud_user.update_user(mock_db, user)
    
    # Assert: Verify database operations were called correctly
    mock_db.add.assert_called_once_with(user)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(user)
    # No attribute assertions, as result is a MagicMock 