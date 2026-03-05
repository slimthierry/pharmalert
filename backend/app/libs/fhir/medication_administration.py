"""
FHIR R4 MedicationAdministration resource endpoint.
Maps internal Administration model to/from FHIR MedicationAdministration.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser, DbSession
from app.models.administration_models import Administration, AdministrationStatus
from app.models.prescription_models import Prescription
from app.schemas.fhir_schemas import (
    FHIRBundle,
    FHIRBundleEntry,
    FHIRCodeableConcept,
    FHIRMedicationAdministration,
    FHIRReference,
)

router = APIRouter()

STATUS_MAP = {
    AdministrationStatus.GIVEN: "completed",
    AdministrationStatus.REFUSED: "not-done",
    AdministrationStatus.MISSED: "not-done",
    AdministrationStatus.DELAYED: "in-progress",
}


def administration_to_fhir(admin: Administration) -> FHIRMedicationAdministration:
    """Convert an internal Administration to a FHIR MedicationAdministration."""
    medication_concept = None
    if admin.prescription and admin.prescription.medication:
        medication_concept = FHIRCodeableConcept(
            text=admin.prescription.medication.name,
        )

    performers = []
    if admin.nurse:
        performers.append({
            "actor": {
                "reference": f"Practitioner/{admin.nurse_id}",
                "display": admin.nurse.name,
            }
        })

    dosage = None
    if admin.dose_given:
        dosage = {
            "dose": {
                "value": admin.dose_given,
                "unit": admin.prescription.dosage_unit if admin.prescription else "mg",
            }
        }

    return FHIRMedicationAdministration(
        id=str(admin.id),
        status=STATUS_MAP.get(admin.status, "unknown"),
        medicationCodeableConcept=medication_concept,
        subject=FHIRReference(
            reference=f"Patient/{admin.patient_ipp}",
        ),
        performer=performers if performers else None,
        effectiveDateTime=admin.administered_at or admin.scheduled_at,
        dosage=dosage,
        request=FHIRReference(
            reference=f"MedicationRequest/{admin.prescription_id}",
        ),
    )


@router.get("/", response_model=FHIRBundle)
async def search_medication_administrations(
    db: DbSession,
    current_user: CurrentUser,
    patient: Optional[str] = None,
    status: Optional[str] = None,
    _count: int = 50,
    _offset: int = 0,
):
    """FHIR search for MedicationAdministration resources."""
    query = select(Administration).options(
        selectinload(Administration.prescription).selectinload(Prescription.medication),
        selectinload(Administration.nurse),
    )

    if patient:
        query = query.where(Administration.patient_ipp == patient)
    if status:
        reverse_map = {v: k for k, v in STATUS_MAP.items()}
        internal_status = reverse_map.get(status)
        if internal_status:
            query = query.where(Administration.status == internal_status)

    result = await db.execute(query.offset(_offset).limit(_count))
    admins = result.scalars().all()

    entries = [
        FHIRBundleEntry(
            resource=administration_to_fhir(a).model_dump(),
            fullUrl=f"MedicationAdministration/{a.id}",
        )
        for a in admins
    ]

    return FHIRBundle(type="searchset", total=len(entries), entry=entries)


@router.get("/{resource_id}", response_model=FHIRMedicationAdministration)
async def read_medication_administration(
    resource_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """FHIR read for a specific MedicationAdministration resource."""
    result = await db.execute(
        select(Administration)
        .options(
            selectinload(Administration.prescription).selectinload(Prescription.medication),
            selectinload(Administration.nurse),
        )
        .where(Administration.id == resource_id)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MedicationAdministration not found",
        )

    return administration_to_fhir(admin)
