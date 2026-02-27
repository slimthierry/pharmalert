"""
FHIR R4 MedicationRequest resource endpoint.
Maps internal Prescription model to/from FHIR MedicationRequest.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import CurrentUser, DbSession
from app.models.prescription_models import Prescription, PrescriptionStatus
from app.schemas.fhir_schemas import (
    FHIRBundle,
    FHIRBundleEntry,
    FHIRCodeableConcept,
    FHIRCoding,
    FHIRDosageInstruction,
    FHIRMedicationRequest,
    FHIRReference,
)

router = APIRouter()

# Status mapping from internal to FHIR
STATUS_MAP = {
    PrescriptionStatus.ACTIVE: "active",
    PrescriptionStatus.COMPLETED: "completed",
    PrescriptionStatus.SUSPENDED: "on-hold",
    PrescriptionStatus.CANCELLED: "cancelled",
}


def prescription_to_fhir(prescription: Prescription) -> FHIRMedicationRequest:
    """Convert an internal Prescription to a FHIR MedicationRequest."""
    medication_concept = None
    if prescription.medication:
        codings = [
            FHIRCoding(
                system="http://www.whocc.no/atc",
                code=prescription.medication.atc_code,
                display=prescription.medication.name,
            )
        ]
        medication_concept = FHIRCodeableConcept(
            coding=codings,
            text=prescription.medication.name,
        )

    dosage_instruction = FHIRDosageInstruction(
        text=f"{prescription.dosage_value} {prescription.dosage_unit} {prescription.frequency}",
        route=FHIRCodeableConcept(
            text=prescription.route.value,
        ),
    )

    return FHIRMedicationRequest(
        id=str(prescription.id),
        status=STATUS_MAP.get(prescription.status, "unknown"),
        intent="order",
        medicationCodeableConcept=medication_concept,
        subject=FHIRReference(
            reference=f"Patient/{prescription.patient_ipp}",
            display=prescription.patient_name,
        ),
        requester=FHIRReference(
            reference=f"Practitioner/{prescription.prescriber_id}",
            display=prescription.prescriber.name if prescription.prescriber else None,
        ),
        dosageInstruction=[dosage_instruction],
        authoredOn=prescription.created_at,
    )


@router.get("/", response_model=FHIRBundle)
async def search_medication_requests(
    db: DbSession,
    current_user: CurrentUser,
    patient: Optional[str] = None,
    status: Optional[str] = None,
    _count: int = 50,
    _offset: int = 0,
):
    """FHIR search for MedicationRequest resources."""
    query = select(Prescription).options(
        selectinload(Prescription.prescriber),
        selectinload(Prescription.medication),
    )

    if patient:
        query = query.where(Prescription.patient_ipp == patient)
    if status:
        # Reverse map FHIR status to internal
        reverse_map = {v: k for k, v in STATUS_MAP.items()}
        internal_status = reverse_map.get(status)
        if internal_status:
            query = query.where(Prescription.status == internal_status)

    result = await db.execute(query.offset(_offset).limit(_count))
    prescriptions = result.scalars().all()

    entries = [
        FHIRBundleEntry(
            resource=prescription_to_fhir(p).model_dump(),
            fullUrl=f"MedicationRequest/{p.id}",
        )
        for p in prescriptions
    ]

    return FHIRBundle(
        type="searchset",
        total=len(entries),
        entry=entries,
    )


@router.get("/{resource_id}", response_model=FHIRMedicationRequest)
async def read_medication_request(
    resource_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """FHIR read for a specific MedicationRequest resource."""
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.prescriber),
            selectinload(Prescription.medication),
        )
        .where(Prescription.id == resource_id)
    )
    prescription = result.scalar_one_or_none()

    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MedicationRequest not found",
        )

    return prescription_to_fhir(prescription)
