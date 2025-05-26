# tests/test_currency.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_currency_conversion():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Precondición: Usuario está registrado y logueado
        await ac.post("/auth/register/", json={"username": "user_a"})
        
        # Login con el usuario A
        resp = await ac.post(
            "/auth/token/",
            data={"username": "user_a", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = resp.json()["access_token"]
        
        # Hacer conversión de moneda
        convert_data = {
            "from_currency": "USD",
            "to_currency": "PEN",
            "amount": 50.0
        }
        convert_resp = await ac.post(
            "/transfer/convert/",
            json=convert_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert convert_resp.status_code == 200
        convert_message = convert_resp.json()["message"]
        assert "convirtió" in convert_message
