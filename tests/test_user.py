import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_balance():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login primero para obtener token
        login_resp = await ac.post(
            "/auth/token/",
            data={"username": "alice", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # Consultar saldo
        balance_resp = await ac.get(
            "/users/me/balance/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert balance_resp.status_code == 200
        balance = balance_resp.json()
        assert "balance_pen" in balance
        assert "balance_usd" in balance
