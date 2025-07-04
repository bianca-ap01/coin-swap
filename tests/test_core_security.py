import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from jose import JWTError
from fastapi import HTTPException
from app.core import security

# Test JWT token creation functionality
def test_create_access_token_with_default_expiry():
    """Test creating JWT token with default expiration time"""
    data = {"sub": "testuser"}
    token = security.create_access_token(data)
    
    # Verify token is created and is a string
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_with_custom_expiry():
    """Test creating JWT token with custom expiration time"""
    data = {"sub": "testuser"}
    custom_expiry = timedelta(hours=2)
    token = security.create_access_token(data, expires_delta=custom_expiry)
    
    # Verify token is created
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_with_additional_data():
    """Test creating JWT token with additional payload data"""
    data = {"sub": "testuser", "role": "admin", "permissions": ["read", "write"]}
    token = security.create_access_token(data)
    
    # Verify token is created
    assert isinstance(token, str)
    assert len(token) > 0

# Test JWT token validation and user retrieval
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test successful user retrieval with valid JWT token"""
    with patch('app.core.security.oauth2_scheme') as mock_oauth2, \
         patch('app.core.security.get_db') as mock_get_db, \
         patch('app.core.security.get_user_by_username') as mock_get_user:
        mock_oauth2.return_value = "valid.jwt.token"
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_get_user.return_value = mock_user
        with patch('app.core.security.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {"sub": "testuser", "exp": datetime.utcnow().timestamp()}
            # Call the function with explicit arguments
            result = await security.get_current_user(token="valid.jwt.token", db=mock_db)
            assert result == mock_user
            mock_jwt_decode.assert_called_once_with("valid.jwt.token", security.SECRET_KEY, algorithms=[security.ALGORITHM])
            mock_get_user.assert_called_once_with(mock_db, "testuser")

@pytest.mark.asyncio
async def test_get_current_user_invalid_token_jwt_error():
    """Test handling of invalid JWT token that causes JWTError"""
    with patch('app.core.security.oauth2_scheme') as mock_oauth2, \
         patch('app.core.security.get_db') as mock_get_db:
        mock_oauth2.return_value = "invalid.jwt.token"
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        with patch('app.core.security.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.side_effect = JWTError("Invalid token")
            with pytest.raises(HTTPException) as exc_info:
                await security.get_current_user(token="invalid.jwt.token", db=mock_db)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "No autenticado"

@pytest.mark.asyncio
async def test_get_current_user_missing_username():
    """Test handling of JWT token with missing username in payload"""
    with patch('app.core.security.oauth2_scheme') as mock_oauth2, \
         patch('app.core.security.get_db') as mock_get_db:
        mock_oauth2.return_value = "valid.jwt.token"
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        with patch('app.core.security.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {"exp": datetime.utcnow().timestamp()}  # No "sub" field
            with pytest.raises(HTTPException) as exc_info:
                await security.get_current_user(token="valid.jwt.token", db=mock_db)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "No autenticado"

@pytest.mark.asyncio
async def test_get_current_user_none_username():
    """Test handling of JWT token with None username in payload"""
    with patch('app.core.security.oauth2_scheme') as mock_oauth2, \
         patch('app.core.security.get_db') as mock_get_db:
        mock_oauth2.return_value = "valid.jwt.token"
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        with patch('app.core.security.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {"sub": None, "exp": datetime.utcnow().timestamp()}
            with pytest.raises(HTTPException) as exc_info:
                await security.get_current_user(token="valid.jwt.token", db=mock_db)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "No autenticado"

@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    """Test handling when user is not found in database"""
    with patch('app.core.security.oauth2_scheme') as mock_oauth2, \
         patch('app.core.security.get_db') as mock_get_db, \
         patch('app.core.security.get_user_by_username') as mock_get_user:
        mock_oauth2.return_value = "valid.jwt.token"
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = None  # User not found
        with patch('app.core.security.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {"sub": "nonexistentuser", "exp": datetime.utcnow().timestamp()}
            with pytest.raises(HTTPException) as exc_info:
                await security.get_current_user(token="valid.jwt.token", db=mock_db)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "No autenticado"
            mock_get_user.assert_called_once_with(mock_db, "nonexistentuser") 