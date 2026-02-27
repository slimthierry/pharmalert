import pytest
from httpx import AsyncClient

from app.models.user_models import User
from tests.conftest import get_auth_headers


class TestDashboard:
    """Test dashboard endpoints."""

    @pytest.mark.asyncio
    async def test_get_dashboard(self, client: AsyncClient, doctor_user: User):
        headers = get_auth_headers(doctor_user)
        response = await client.get("/api/v1/dashboard/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "alerts" in data
        stats = data["stats"]
        assert "pending_validations" in stats
        assert "critical_interactions" in stats
        assert "missed_doses_today" in stats
        assert "compliance_rate" in stats
        assert "total_active_prescriptions" in stats
        assert "total_patients" in stats

    @pytest.mark.asyncio
    async def test_dashboard_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/dashboard/")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pharmalert"
