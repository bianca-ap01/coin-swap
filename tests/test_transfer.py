# tests/test_transfer.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_transfer():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Precondición: usuario A y B están registrados
        await ac.post("/auth/register/", json={"username": "user_a"})
        await ac.post("/auth/register/", json={"username": "user_b"})
        
        # Login con el usuario A
        resp = await ac.post(
            "/auth/token/",
            data={"username": "user_a", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = resp.json()["access_token"]
        
        # Hacer la transferencia
        transfer_data = {
            "receiver": "user_b",
            "amount": 50.0,
            "currency": "USD"
        }
        transfer_resp = await ac.post(
            "/transfer/transfer/",
            json=transfer_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert transfer_resp.status_code == 200
        transfer_message = transfer_resp.json()["message"]
        assert "transfirió" in transfer_message
