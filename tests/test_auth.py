# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Registrar un usuario
        resp = await ac.post("/auth/register/", json={"username": "testuser"})
        assert resp.status_code == 201

        # Hacer login con el usuario
        resp = await ac.post(
            "/auth/token/",
            data={"username": "testuser", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
