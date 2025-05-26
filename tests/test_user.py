# tests/test_user.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_balance():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Registrar un usuario
        await ac.post("/auth/register/", json={"username": "testuser"})
        
        # Login con el usuario
        resp = await ac.post(
            "/auth/token/",
            data={"username": "testuser", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = resp.json()["access_token"]

        # Consultar saldo
        balance_resp = await ac.get(
            "/users/me/balance/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert balance_resp.status_code == 200
        balance = balance_resp.json()
        assert "balance_pen" in balance
        assert "balance_usd" in balance
