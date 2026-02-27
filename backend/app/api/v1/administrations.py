from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.rbac import require_infirmier
from app.models.administration_models import AdministrationStatus
from app.models.user_models import User
from app.schemas.administration_schemas import (
    AdministrationCreate,
    AdministrationListResponse,
    AdministrationRecord,
    AdministrationResponse,
)
from app.services.administration_service import (
    create_administration,
    get_administration,
    get_today_schedule,
    list_administrations,
    record_administration,
)

router = APIRouter()


@router.get("/", response_model=AdministrationListResponse)
async def get_administrations(
    db: DbSession,
    current_user: CurrentUser,
    patient_ipp: Optional[str] = None,
    status: Optional[AdministrationStatus] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List administrations with optional filters."""
    administrations, total = await list_administrations(
        db, patient_ipp=patient_ipp, status=status, skip=skip, limit=limit
    )

    responses = []
    for a in administrations:
        responses.append(
            AdministrationResponse(
                id=a.id,
                prescription_id=a.prescription_id,
                nurse_id=a.nurse_id,
                nurse_name=a.nurse.name if a.nurse else None,
                scheduled_at=a.scheduled_at,
                administered_at=a.administered_at,
                dose_given=a.dose_given,
                status=a.status,
                patient_ipp=a.patient_ipp,
                patient_name=a.prescription.patient_name if a.prescription else None,
                medication_name=(
                    a.prescription.medication.name
                    if a.prescription and a.prescription.medication
                    else None
                ),
                notes=a.notes,
                vital_signs=a.vital_signs,
                created_at=a.created_at,
            )
        )

    return AdministrationListResponse(administrations=responses, total=total)


@router.get("/today", response_model=list[AdministrationResponse])
async def get_today_administrations(
    db: DbSession,
    current_user: CurrentUser,
):
    """Get today's administration schedule for the current nurse."""
    administrations = await get_today_schedule(db, nurse_id=current_user.id)

    return [
        AdministrationResponse(
            id=a.id,
            prescription_id=a.prescription_id,
            nurse_id=a.nurse_id,
            nurse_name=a.nurse.name if a.nurse else None,
            scheduled_at=a.scheduled_at,
            administered_at=a.administered_at,
            dose_given=a.dose_given,
            status=a.status,
            patient_ipp=a.patient_ipp,
            patient_name=a.prescription.patient_name if a.prescription else None,
            medication_name=(
                a.prescription.medication.name
                if a.prescription and a.prescription.medication
                else None
            ),
            notes=a.notes,
            vital_signs=a.vital_signs,
            created_at=a.created_at,
        )
        for a in administrations
    ]


@router.get("/{administration_id}", response_model=AdministrationResponse)
async def get_administration_by_id(
    administration_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific administration by ID."""
    administration = await get_administration(db, administration_id)
    if not administration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administration non trouvee",
        )
    return AdministrationResponse(
        id=administration.id,
        prescription_id=administration.prescription_id,
        nurse_id=administration.nurse_id,
        nurse_name=administration.nurse.name if administration.nurse else None,
        scheduled_at=administration.scheduled_at,
        administered_at=administration.administered_at,
        dose_given=administration.dose_given,
        status=administration.status,
        patient_ipp=administration.patient_ipp,
        patient_name=(
            administration.prescription.patient_name
            if administration.prescription
            else None
        ),
        medication_name=(
            administration.prescription.medication.name
            if administration.prescription and administration.prescription.medication
            else None
        ),
        notes=administration.notes,
        vital_signs=administration.vital_signs,
        created_at=administration.created_at,
    )


@router.post("/", response_model=AdministrationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_administration(
    data: AdministrationCreate,
    db: DbSession,
    current_user: User = Depends(require_infirmier),
):
    """Schedule a new administration (nurse only)."""
    administration = await create_administration(db, data)
    return AdministrationResponse(
        id=administration.id,
        prescription_id=administration.prescription_id,
        nurse_id=administration.nurse_id,
        scheduled_at=administration.scheduled_at,
        administered_at=administration.administered_at,
        dose_given=administration.dose_given,
        status=administration.status,
        patient_ipp=administration.patient_ipp,
        notes=administration.notes,
        vital_signs=administration.vital_signs,
        created_at=administration.created_at,
    )


@router.post("/{administration_id}/record", response_model=AdministrationResponse)
async def record_administration_by_id(
    administration_id: int,
    record: AdministrationRecord,
    db: DbSession,
    current_user: User = Depends(require_infirmier),
):
    """Record an administration (nurse marks dose as given/refused/missed/delayed)."""
    administration = await record_administration(
        db, administration_id, record, current_user
    )
    if not administration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administration non trouvee",
        )
    return AdministrationResponse(
        id=administration.id,
        prescription_id=administration.prescription_id,
        nurse_id=administration.nurse_id,
        nurse_name=current_user.name,
        scheduled_at=administration.scheduled_at,
        administered_at=administration.administered_at,
        dose_given=administration.dose_given,
        status=administration.status,
        patient_ipp=administration.patient_ipp,
        notes=administration.notes,
        vital_signs=administration.vital_signs,
        created_at=administration.created_at,
    )
