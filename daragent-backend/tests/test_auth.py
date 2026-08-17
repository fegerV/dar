"""Integration tests for authentication flow."""
import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User",
}


class TestAuthFlow:
    @pytest.mark.asyncio
    async def test_register_creates_user(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["is_admin"] is True
        assert data["user"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        refresh_token = reg.json()["refresh_token"]

        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid-token",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        token = reg.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_via_refresh_revoke(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        refresh_token = reg.json()["refresh_token"]

        # Use refresh token once
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200

        # Using the same refresh token again should fail (single use)
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 401
