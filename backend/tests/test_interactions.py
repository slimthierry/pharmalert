import pytest
from httpx import AsyncClient

from app.models.interaction_models import Interaction
from app.models.medication_models import Medication
from app.models.user_models import User
from tests.conftest import get_auth_headers


class TestInteractions:
    """Test interaction checking endpoints."""

    @pytest.mark.asyncio
    async def test_list_interactions(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_interaction: Interaction,
    ):
        headers = get_auth_headers(doctor_user)
        response = await client.get("/api/v1/interactions/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["interactions"]) >= 1

    @pytest.mark.asyncio
    async def test_get_interaction(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_interaction: Interaction,
    ):
        headers = get_auth_headers(doctor_user)
        response = await client.get(
            f"/api/v1/interactions/{sample_interaction.id}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == "major"
        assert "hemorragique" in data["clinical_effect"].lower()

    @pytest.mark.asyncio
    async def test_check_interactions(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
        sample_interaction: Interaction,
    ):
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/interactions/check",
            headers=headers,
            json={
                "medication_ids": [
                    sample_medications[0].id,
                    sample_medications[1].id,
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_major"] is True
        assert len(data["interactions"]) >= 1

    @pytest.mark.asyncio
    async def test_check_no_interactions(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
    ):
        headers = get_auth_headers(doctor_user)
        # Warfarine + Omeprazole (no interaction in fixtures)
        response = await client.post(
            "/api/v1/interactions/check",
            headers=headers,
            json={
                "medication_ids": [
                    sample_medications[0].id,
                    sample_medications[2].id,
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_major"] is False
        assert data["has_contraindicated"] is False

    @pytest.mark.asyncio
    async def test_create_interaction(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
    ):
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/interactions/",
            headers=headers,
            json={
                "medication_a_id": sample_medications[0].id,
                "medication_b_id": sample_medications[2].id,
                "severity": "moderate",
                "clinical_effect": "Diminution de l'absorption de la warfarine",
                "recommendation": "Espacer les prises de 2 heures minimum",
                "source": "Thesaurus ANSM",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "moderate"
