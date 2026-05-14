"""Tests for patient allergy management endpoints."""

import pytest
from httpx import AsyncClient

from app.models.allergy_models import (
    PatientAllergy,
    AllergenType,
    AllergySeverity,
    ReactionType,
)
from app.models.user_models import User
from tests.conftest import get_auth_headers


async def create_allergy(db_session, **overrides):
    """Helper to create a patient allergy in the test database."""
    allergy = PatientAllergy(
        patient_ipp=overrides.get("patient_ipp", "IPP_ALG_TEST"),
        allergen_type=overrides.get("allergen_type", AllergenType.MEDICATION),
        allergen_name=overrides.get("allergen_name", "Penicilline"),
        atc_code=overrides.get("atc_code", "J01CE01"),
        severity=overrides.get("severity", AllergySeverity.SEVERE),
        reaction_type=overrides.get("reaction_type", ReactionType.RASH),
        confirmed=overrides.get("confirmed", False),
    )
    db_session.add(allergy)
    await db_session.commit()
    await db_session.refresh(allergy)
    return allergy


class TestAllergies:
    """Test patient allergy endpoints."""

    @pytest.mark.asyncio
    async def test_list_allergies(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test listing all patient allergies."""
        await create_allergy(db_session, patient_ipp="IPP_ALG_LST")
        headers = get_auth_headers(doctor_user)
        response = await client.get("/api/v1/allergies/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "allergies" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_allergies_by_patient(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test filtering allergies by patient IPP."""
        await create_allergy(db_session, patient_ipp="IPP_ALG_PAT", allergen_name="Aspirine")
        headers = get_auth_headers(doctor_user)
        response = await client.get(
            "/api/v1/allergies/?patient_ipp=IPP_ALG_PAT",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert all(a["patient_ipp"] == "IPP_ALG_PAT" for a in data["allergies"])

    @pytest.mark.asyncio
    async def test_get_patient_allergies(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test getting all allergies for a specific patient."""
        await create_allergy(db_session, patient_ipp="IPP_ALG_GET", allergen_name="Amoxicilline")
        headers = get_auth_headers(doctor_user)
        response = await client.get(
            "/api/v1/allergies/patient/IPP_ALG_GET",
            headers=headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_create_allergy(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test creating a new patient allergy record."""
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/allergies/",
            headers=headers,
            json={
                "patient_ipp": "IPP_NEW_ALG",
                "allergen_type": "medication",
                "allergen_name": "Ibuprofene",
                "atc_code": "M01AE01",
                "severity": "moderate",
                "reaction_type": "rash",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["patient_ipp"] == "IPP_NEW_ALG"
        assert data["allergen_name"] == "Ibuprofene"
        assert data["severity"] == "moderate"

    @pytest.mark.asyncio
    async def test_create_allergy_life_threatening(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test creating a life-threatening allergy (contraindication signal)."""
        headers = get_auth_headers(doctor_user)
        response = await client.post(
            "/api/v1/allergies/",
            headers=headers,
            json={
                "patient_ipp": "IPP_LTH_001",
                "allergen_type": "medication",
                "allergen_name": "Sulfamides",
                "severity": "life_threatening",
                "reaction_type": "anaphylaxis",
                "confirmed": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "life_threatening"
        assert data["confirmed"] is True

    @pytest.mark.asyncio
    async def test_delete_allergy(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test deleting an allergy record."""
        allergy = await create_allergy(db_session, patient_ipp="IPP_DEL_001")
        headers = get_auth_headers(doctor_user)
        response = await client.delete(
            f"/api/v1/allergies/{allergy.id}",
            headers=headers,
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_allergy_not_found(
        self,
        client: AsyncClient,
        doctor_user: User,
    ):
        """Test deleting non-existent allergy returns 404."""
        headers = get_auth_headers(doctor_user)
        response = await client.delete(
            "/api/v1/allergies/99999",
            headers=headers,
        )
        assert response.status_code == 404