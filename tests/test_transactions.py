# tests/test_transactions.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_transaction_history():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Registrar dos usuarios
        await ac.post("/auth/register/", json={"username": "user_a"})
        await ac.post("/auth/register/", json={"username": "user_b"})

        # Login con el usuario A
        resp = await ac.post(
            "/auth/token/",
            data={"username": "user_a", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = resp.json()["access_token"]

        # Realizar una transferencia de usuario A a B
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
        
        # Obtener el historial de transacciones de A
        history_resp_a = await ac.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert history_resp_a.status_code == 200
        history_a = history_resp_a.json()
        assert len(history_a) > 0
        assert "transfirió" in history_a[0]["description"]
        
        # Login con el usuario B
        resp_b = await ac.post(
            "/auth/token/",
            data={"username": "user_b", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_b = resp_b.json()["access_token"]
        
        # Obtener el historial de transacciones de B
        history_resp_b = await ac.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert history_resp_b.status_code == 200
        history_b = history_resp_b.json()
        assert len(history_b) > 0
        assert "recibió" in history_b[0]["description"]
