# tests/test_deposit_withdraw.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_deposit():
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

        # Realizar un depósito
        deposit_data = {
            "amount": 50.0,
            "currency": "USD",
            "operation": "deposit"
        }
        deposit_resp = await ac.post(
            "/transfer/user/balance/change/",
            json=deposit_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert deposit_resp.status_code == 200
        deposit_message = deposit_resp.json()["message"]
        assert "depositó" in deposit_message

        # Verificar que el saldo se ha actualizado
        balance_resp = await ac.get(
            "/users/me/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert balance_resp.status_code == 200
        balance = balance_resp.json()
        assert balance["balance_usd"] == 50.0

@pytest.mark.asyncio
async def test_withdraw():
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

        # Realizar un depósito primero
        deposit_data = {
            "amount": 50.0,
            "currency": "USD",
            "operation": "deposit"
        }
        await ac.post(
            "/transfer/user/balance/change/",
            json=deposit_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Realizar un retiro
        withdraw_data = {
            "amount": 20.0,
            "currency": "USD",
            "operation": "withdraw"
        }
        withdraw_resp = await ac.post(
            "/transfer/user/balance/change/",
            json=withdraw_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert withdraw_resp.status_code == 200
        withdraw_message = withdraw_resp.json()["message"]
        assert "retiró" in withdraw_message

        # Verificar que el saldo se ha actualizado
        balance_resp = await ac.get(
            "/users/me/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert balance_resp.status_code == 200
        balance = balance_resp.json()
        assert balance["balance_usd"] == 30.0  # 50 depositados - 20 retirados

@pytest.mark.asyncio
async def test_withdraw_insufficient_balance():
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

        # Intentar retirar más dinero del que tiene el usuario
        withdraw_data = {
            "amount": 100.0,  # Intentar retirar 100, pero el saldo inicial es 0
            "currency": "USD",
            "operation": "withdraw"
        }
        withdraw_resp = await ac.post(
            "/transfer/user/balance/change/",
            json=withdraw_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert withdraw_resp.status_code == 400
        error_message = withdraw_resp.json()["detail"]
        assert "Saldo insuficiente en USD para retiro" in error_message
