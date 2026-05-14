"""Tests for medication administration endpoints."""

import pytest
from datetime import datetime, date, timedelta, timezone
from httpx import AsyncClient

from app.models.administration_models import Administration, AdministrationStatus
from app.models.prescription_models import Prescription
from app.models.medication_models import Medication
from app.models.user_models import User
from tests.conftest import get_auth_headers


async def create_prescription(db_session, doctor: User, medication: Medication, **overrides):
    """Helper to create a prescription in the test database."""
    rx = Prescription(
        patient_ipp=overrides.get("patient_ipp", "IPP_ADM_TEST"),
        patient_name=overrides.get("patient_name", "Jean Admin"),
        doctor_id=doctor.id,
        medication_id=medication.id,
        dosage_value=overrides.get("dosage_value", 10.0),
        dosage_unit=overrides.get("dosage_unit", "mg"),
        frequency=overrides.get("frequency", "2x/day"),
        route=overrides.get("route", "oral"),
        start_date=date.today(),
        status="active",
        validation_status="validated",
        interactions_checked=True,
    )
    db_session.add(rx)
    await db_session.commit()
    await db_session.refresh(rx)
    return rx


async def create_administration(db_session, prescription: Prescription, nurse: User, **overrides):
    """Helper to create an administration record."""
    admin = Administration(
        prescription_id=prescription.id,
        nurse_id=nurse.id,
        patient_ipp=prescription.patient_ipp,
        scheduled_at=overrides.get("scheduled_at", datetime.now(timezone.utc)),
        administered_at=overrides.get("administered_at"),
        dose_given=overrides.get("dose_given"),
        status=overrides.get("status", AdministrationStatus.GIVEN),
        notes=overrides.get("notes"),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


class TestAdministrations:
    """Test administration endpoints."""

    @pytest.mark.asyncio
    async def test_list_administrations(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test listing all administrations."""
        rx = await create_prescription(db_session, doctor_user, sample_medications[0])
        await create_administration(db_session, rx, nurse_user)
        headers = get_auth_headers(nurse_user)
        response = await client.get("/api/v1/administrations/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "administrations" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_administrations_by_patient(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test filtering administrations by patient IPP."""
        rx = await create_prescription(
            db_session, doctor_user, sample_medications[0], patient_ipp="IPP_ADM_PAT"
        )
        await create_administration(db_session, rx, nurse_user)
        headers = get_auth_headers(nurse_user)
        response = await client.get(
            "/api/v1/administrations/?patient_ipp=IPP_ADM_PAT",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert all(a["patient_ipp"] == "IPP_ADM_PAT" for a in data["administrations"])

    @pytest.mark.asyncio
    async def test_today_administrations(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test getting today's administrations."""
        rx = await create_prescription(db_session, doctor_user, sample_medications[0])
        await create_administration(
            db_session, rx, nurse_user,
            scheduled_at=datetime.now(timezone.utc),
        )
        headers = get_auth_headers(nurse_user)
        response = await client.get("/api/v1/administrations/today", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_record_administration_given(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test recording a successful medication administration."""
        rx = await create_prescription(
            db_session, doctor_user, sample_medications[0],
            dosage_value=20.0,
        )
        admin = await create_administration(
            db_session, rx, nurse_user,
            administered_at=None,
            dose_given=None,
            status=AdministrationStatus.GIVEN,
        )
        headers = get_auth_headers(nurse_user)
        response = await client.post(
            f"/api/v1/administrations/{admin.id}/record",
            headers=headers,
            json={
                "status": "given",
                "dose_given": 20.0,
                "notes": "Patient bien tolere",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "given"
        assert data["dose_given"] == 20.0

    @pytest.mark.asyncio
    async def test_record_administration_refused(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test recording a refused medication administration."""
        rx = await create_prescription(db_session, doctor_user, sample_medications[0])
        admin = await create_administration(
            db_session, rx, nurse_user,
            administered_at=None, dose_given=None,
        )
        headers = get_auth_headers(nurse_user)
        response = await client.post(
            f"/api/v1/administrations/{admin.id}/record",
            headers=headers,
            json={
                "status": "refused",
                "notes": "Patient refuse le medicament",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "refused"

    @pytest.mark.asyncio
    async def test_record_administration_not_found(
        self,
        client: AsyncClient,
        nurse_user: User,
    ):
        """Test recording for non-existent administration returns 404."""
        headers = get_auth_headers(nurse_user)
        response = await client.post(
            "/api/v1/administrations/99999/record",
            headers=headers,
            json={"status": "given"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_administration_audit_trail(
        self,
        client: AsyncClient,
        doctor_user: User,
        nurse_user: User,
        sample_medications: list[Medication],
        db_session,
    ):
        """Test that administrations create audit log entries."""
        rx = await create_prescription(db_session, doctor_user, sample_medications[0])
        admin = await create_administration(db_session, rx, nurse_user)
        headers = get_auth_headers(nurse_user)

        # Record administration
        await client.post(
            f"/api/v1/administrations/{admin.id}/record",
            headers=headers,
            json={"status": "given", "dose_given": 10.0},
        )

        # Check audit log
        response = await client.get("/api/v1/audit/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
