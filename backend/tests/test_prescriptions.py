import pytest
from datetime import date
from httpx import AsyncClient

from app.models.interaction_models import Interaction, InteractionSeverity
from app.models.medication_models import Medication
from app.models.user_models import User
from tests.conftest import get_auth_headers


class TestPrescriptions:
    """Test prescription endpoints with interaction checking."""

    @pytest.mark.asyncio
    async def test_create_prescription(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
    ):
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/prescriptions/",
            headers=headers,
            json={
                "patient_ipp": "IPP001",
                "patient_name": "Jean Dupont",
                "medication_id": sample_medications[2].id,  # Omeprazole
                "dosage_value": 20.0,
                "dosage_unit": "mg",
                "frequency": "1x/day",
                "route": "oral",
                "start_date": str(date.today()),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["prescription"]["patient_ipp"] == "IPP001"
        assert data["prescription"]["validation_status"] == "pending"
        assert data["prescription"]["interactions_checked"] is True

    @pytest.mark.asyncio
    async def test_create_prescription_nurse_forbidden(
        self,
        client: AsyncClient,
        nurse_user: User,
        sample_medications: list[Medication],
    ):
        headers = get_auth_headers(nurse_user)
        response = await client.post(
            "/api/v1/prescriptions/",
            headers=headers,
            json={
                "patient_ipp": "IPP001",
                "patient_name": "Jean Dupont",
                "medication_id": sample_medications[0].id,
                "dosage_value": 5.0,
                "dosage_unit": "mg",
                "frequency": "1x/day",
                "route": "oral",
                "start_date": str(date.today()),
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_validate_prescription_pharmacist(
        self,
        client: AsyncClient,
        doctor_user: User,
        pharmacist_user: User,
        sample_medications: list[Medication],
    ):
        # Create prescription
        doc_headers = get_auth_headers(doctor_user)
        create_resp = await client.post(
            "/api/v1/prescriptions/",
            headers=doc_headers,
            json={
                "patient_ipp": "IPP002",
                "patient_name": "Marie Martin",
                "medication_id": sample_medications[2].id,
                "dosage_value": 20.0,
                "dosage_unit": "mg",
                "frequency": "1x/day",
                "route": "oral",
                "start_date": str(date.today()),
            },
        )
        assert create_resp.status_code == 201
        prescription_id = create_resp.json()["prescription"]["id"]

        # Validate as pharmacist
        pharm_headers = get_auth_headers(pharmacist_user)
        validate_resp = await client.post(
            f"/api/v1/prescriptions/{prescription_id}/validate",
            headers=pharm_headers,
            json={
                "validation_status": "validated",
                "validation_notes": "Posologie correcte",
            },
        )
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert data["validation_status"] == "validated"

    @pytest.mark.asyncio
    async def test_validate_prescription_doctor_forbidden(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
    ):
        # Create prescription
        headers = get_auth_headers(doctor_user)
        create_resp = await client.post(
            "/api/v1/prescriptions/",
            headers=headers,
            json={
                "patient_ipp": "IPP003",
                "patient_name": "Pierre Durand",
                "medication_id": sample_medications[0].id,
                "dosage_value": 5.0,
                "dosage_unit": "mg",
                "frequency": "1x/day",
                "route": "oral",
                "start_date": str(date.today()),
            },
        )
        prescription_id = create_resp.json()["prescription"]["id"]

        # Doctor tries to validate (forbidden)
        validate_resp = await client.post(
            f"/api/v1/prescriptions/{prescription_id}/validate",
            headers=headers,
            json={"validation_status": "validated"},
        )
        assert validate_resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_prescriptions(
        self,
        client: AsyncClient,
        doctor_user: User,
        sample_medications: list[Medication],
    ):
        headers = get_auth_headers(doctor_user)

        # Create a prescription first
        await client.post(
            "/api/v1/prescriptions/",
            headers=headers,
            json={
                "patient_ipp": "IPP004",
                "patient_name": "Sophie Bernard",
                "medication_id": sample_medications[0].id,
                "dosage_value": 5.0,
                "dosage_unit": "mg",
                "frequency": "1x/day",
                "route": "oral",
                "start_date": str(date.today()),
            },
        )

        response = await client.get("/api/v1/prescriptions/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
