import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.crud import transaction as crud_transaction

import datetime
import asyncio

@pytest.mark.asyncio
async def test_insert_transaction():
    """Test inserting a new transaction record into MongoDB"""
    # Arrange: Mock the MongoDB collection
    with patch('app.crud.transaction.transactions_collection') as mock_collection:
        mock_insert = AsyncMock()
        mock_collection.insert_one = mock_insert
        
        # Act: Call the async function under test
        await crud_transaction.insert_transaction('desc', 'user1')
        
        # Assert: Verify the async operation was called and check arguments
        assert mock_insert.await_count == 1
        # Check the call arguments directly
        call_args = mock_insert.await_args
        assert call_args is not None
        args, kwargs = call_args
        assert args[0]['description'] == 'desc'
        assert args[0]['username'] == 'user1'
        assert 'timestamp' in args[0]

@pytest.mark.asyncio
async def test_get_transactions_by_user():
    """Test retrieving all transactions for a specific user from MongoDB"""
    # Arrange: Mock the MongoDB collection and TransactionOut model
    with patch('app.crud.transaction.transactions_collection') as mock_collection, \
         patch('app.crud.transaction.TransactionOut') as MockTransactionOut:
        # Mock the async cursor with sample transaction data
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = [
            {'timestamp': datetime.datetime.utcnow(), 'description': 'desc1', 'username': 'user1'},
            {'timestamp': datetime.datetime.utcnow(), 'description': 'desc2', 'username': 'user1'}
        ]
        mock_collection.find.return_value.sort.return_value = mock_cursor
        mock_out_instance = MagicMock()
        MockTransactionOut.side_effect = lambda **kwargs: mock_out_instance
        
        # Act: Call the async function under test
        result = await crud_transaction.get_transactions_by_user('user1')
        
        # Assert: Verify database operations and returned results
        assert mock_collection.find.called
        assert mock_cursor.__aiter__.called
        assert MockTransactionOut.call_count == 2
        assert result == [mock_out_instance, mock_out_instance] 