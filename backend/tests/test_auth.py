import pytest
from httpx import AsyncClient

from app.models.user_models import User
from tests.conftest import get_auth_headers


class TestAuthentication:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@pharmalert.fr", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"
        assert data["name"] == "Admin Test"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, admin_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@pharmalert.fr", "password": "wrong"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@pharmalert.fr", "password": "test123"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@pharmalert.fr"
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_register_user_admin_only(
        self, client: AsyncClient, admin_user: User, doctor_user: User
    ):
        # Admin can register
        headers = get_auth_headers(admin_user)
        response = await client.post(
            "/api/v1/auth/register",
            headers=headers,
            json={
                "email": "new@pharmalert.fr",
                "name": "New User",
                "password": "newuser123",
                "role": "infirmier",
            },
        )
        assert response.status_code == 201

        # Doctor cannot register
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/auth/register",
            headers=headers,
            json={
                "email": "another@pharmalert.fr",
                "name": "Another User",
                "password": "another123",
                "role": "infirmier",
            },
        )
        assert response.status_code == 403
