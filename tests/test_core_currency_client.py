import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core import currency_client
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_exchangerate_api_com_adapter_success():
    """Test successful currency rate retrieval from ExchangeRate-API.com"""
    # Arrange: Mock the HTTP client and response
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"USD": 1.0, "PEN": 3.7}}
        mock_client.get.return_value = mock_response
        
        # Act: Create adapter and get rate
        adapter = currency_client.ExchangeRateApiComAdapter()
        result = await adapter.get_rate("USD", "PEN")
        
        # Assert: Verify correct rate and adapter name
        assert result == 3.7
        assert adapter.name() == "ExchangeRate-API.com (public)"

@pytest.mark.asyncio
async def test_exchangerate_api_com_adapter_unsupported_currency():
    """Test handling of unsupported currency in ExchangeRate-API.com adapter"""
    # Arrange: Mock the HTTP client with limited currency support
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"USD": 1.0}}  # PEN not available
        mock_client.get.return_value = mock_response
        
        # Act & Assert: Verify HTTPException is raised for unsupported currency
        adapter = currency_client.ExchangeRateApiComAdapter()
        with pytest.raises(HTTPException) as exc_info:
            await adapter.get_rate("USD", "INVALID")
        assert exc_info.value.status_code == 400
        assert "INVALID" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_open_er_api_adapter_success():
    """Test successful currency rate retrieval from Open ER API"""
    # Arrange: Mock the HTTP client and response
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success", "rates": {"USD": 1.0, "PEN": 3.7}}
        mock_client.get.return_value = mock_response
        
        # Act: Create adapter and get rate
        adapter = currency_client.OpenERAPIAdapter()
        result = await adapter.get_rate("USD", "PEN")
        
        # Assert: Verify correct rate and adapter name
        assert result == 3.7
        assert adapter.name() == "Open ER API (public)"

@pytest.mark.asyncio
async def test_open_er_api_adapter_failure():
    """Test handling of API failure response from Open ER API"""
    # Arrange: Mock the HTTP client with failure response
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "error"}  # API failure
        mock_client.get.return_value = mock_response
        
        # Act & Assert: Verify HTTPException is raised for API failure
        adapter = currency_client.OpenERAPIAdapter()
        with pytest.raises(HTTPException) as exc_info:
            await adapter.get_rate("USD", "PEN")
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_open_er_api_adapter_unsupported_currency():
    """Test handling of unsupported currency in Open ER API adapter"""
    # Arrange: Mock the HTTP client with limited currency support
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success", "rates": {"USD": 1.0}}  # PEN not available
        mock_client.get.return_value = mock_response
        
        # Act & Assert: Verify HTTPException is raised for unsupported currency
        adapter = currency_client.OpenERAPIAdapter()
        with pytest.raises(HTTPException) as exc_info:
            await adapter.get_rate("USD", "INVALID")
        assert exc_info.value.status_code == 400

def test_currency_api_client_singleton():
    """Test that CurrencyAPIClientSingleton follows the singleton pattern"""
    # Act: Create two instances
    client1 = currency_client.CurrencyAPIClientSingleton()
    client2 = currency_client.CurrencyAPIClientSingleton()
    
    # Assert: Verify both instances are the same object
    assert client1 is client2

def test_currency_api_client_select_adapter():
    """Test switching between different currency API adapters"""
    # Arrange: Get singleton instance
    client = currency_client.CurrencyAPIClientSingleton()
    
    # Act: Switch to different adapter
    client.select_adapter("openerapublic")
    
    # Assert: Verify adapter name reflects the change
    assert client.get_current_adapter_name() == "Open ER API (public)"

def test_currency_api_client_select_invalid_adapter():
    """Test handling of invalid adapter selection"""
    # Arrange: Get singleton instance
    client = currency_client.CurrencyAPIClientSingleton()
    
    # Act & Assert: Verify ValueError is raised for invalid adapter
    with pytest.raises(ValueError) as exc_info:
        client.select_adapter("invalid")
    assert "invalid" in str(exc_info.value)

@pytest.mark.asyncio
async def test_currency_api_client_get_rate():
    """Test getting exchange rate through the singleton client"""
    # Arrange: Mock the HTTP client and set adapter
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"USD": 1.0, "PEN": 3.7}}
        mock_client.get.return_value = mock_response
        client = currency_client.CurrencyAPIClientSingleton()
        # Set to use the adapter we're mocking
        client.select_adapter("exchangerateapi")
        
        # Act: Get rate through singleton
        result = await client.get_rate("USD", "PEN")
        
        # Assert: Verify correct rate is returned
        assert result == 3.7

@pytest.mark.asyncio
async def test_currency_api_client_list_all_rates():
    """Test getting rates from all available adapters"""
    # Arrange: Mock the HTTP client for all adapters
    with patch('app.core.currency_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        # Mock response that works for both adapters
        mock_response.json.return_value = {"result": "success", "rates": {"USD": 1.0, "PEN": 3.7}}
        mock_client.get.return_value = mock_response
        client = currency_client.CurrencyAPIClientSingleton()
        
        # Act: Get rates from all adapters
        result = await client.list_all_rates("USD", "PEN")
        
        # Assert: Verify both adapters returned results
        assert "ExchangeRate-API.com (public)" in result
        assert "Open ER API (public)" in result
        assert isinstance(result["ExchangeRate-API.com (public)"], float)
        assert isinstance(result["Open ER API (public)"], float) 