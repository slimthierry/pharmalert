from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.rbac import require_medecin, require_pharmacien
from app.models.prescription_models import PrescriptionStatus, ValidationStatus
from app.models.user_models import User
from app.schemas.prescription_schemas import (
    PrescriptionCreate,
    PrescriptionCreateResponse,
    PrescriptionListResponse,
    PrescriptionResponse,
    PrescriptionUpdate,
    PrescriptionValidate,
)
from app.services.prescription_service import (
    create_prescription,
    get_prescription,
    list_prescriptions,
    update_prescription,
    validate_prescription,
)

router = APIRouter()


@router.get("/", response_model=PrescriptionListResponse)
async def get_prescriptions(
    db: DbSession,
    current_user: CurrentUser,
    patient_ipp: Optional[str] = None,
    status: Optional[PrescriptionStatus] = None,
    validation_status: Optional[ValidationStatus] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List prescriptions with optional filters."""
    prescriptions, total = await list_prescriptions(
        db,
        patient_ipp=patient_ipp,
        status=status,
        validation_status=validation_status,
        skip=skip,
        limit=limit,
    )

    prescription_responses = []
    for p in prescriptions:
        prescription_responses.append(
            PrescriptionResponse(
                id=p.id,
                patient_ipp=p.patient_ipp,
                patient_name=p.patient_name,
                prescriber_id=p.prescriber_id,
                prescriber_name=p.prescriber.name if p.prescriber else None,
                medication_id=p.medication_id,
                medication_name=p.medication.name if p.medication else None,
                dosage_value=p.dosage_value,
                dosage_unit=p.dosage_unit,
                frequency=p.frequency,
                route=p.route,
                start_date=p.start_date,
                end_date=p.end_date,
                status=p.status,
                validation_status=p.validation_status,
                validated_by=p.validated_by,
                validator_name=p.validator.name if p.validator else None,
                validation_notes=p.validation_notes,
                interactions_checked=p.interactions_checked,
                override_justification=p.override_justification,
                created_at=p.created_at,
            )
        )

    return PrescriptionListResponse(prescriptions=prescription_responses, total=total)


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription_by_id(
    prescription_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific prescription by ID."""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription non trouvee",
        )
    return PrescriptionResponse(
        id=prescription.id,
        patient_ipp=prescription.patient_ipp,
        patient_name=prescription.patient_name,
        prescriber_id=prescription.prescriber_id,
        prescriber_name=prescription.prescriber.name if prescription.prescriber else None,
        medication_id=prescription.medication_id,
        medication_name=prescription.medication.name if prescription.medication else None,
        dosage_value=prescription.dosage_value,
        dosage_unit=prescription.dosage_unit,
        frequency=prescription.frequency,
        route=prescription.route,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        status=prescription.status,
        validation_status=prescription.validation_status,
        validated_by=prescription.validated_by,
        validator_name=prescription.validator.name if prescription.validator else None,
        validation_notes=prescription.validation_notes,
        interactions_checked=prescription.interactions_checked,
        override_justification=prescription.override_justification,
        created_at=prescription.created_at,
    )


@router.post("/", response_model=PrescriptionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_prescription(
    data: PrescriptionCreate,
    db: DbSession,
    current_user: User = Depends(require_medecin),
):
    """
    Create a new prescription (doctor only).
    Automatically checks interactions against all active prescriptions for the patient.
    Blocks if a contraindicated interaction is detected unless override_justification is provided.
    """
    return await create_prescription(db, data, current_user)


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription_by_id(
    prescription_id: int,
    data: PrescriptionUpdate,
    db: DbSession,
    current_user: User = Depends(require_medecin),
):
    """Update a prescription (doctor only)."""
    prescription = await update_prescription(db, prescription_id, data)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription non trouvee",
        )
    return PrescriptionResponse(
        id=prescription.id,
        patient_ipp=prescription.patient_ipp,
        patient_name=prescription.patient_name,
        prescriber_id=prescription.prescriber_id,
        prescriber_name=prescription.prescriber.name if prescription.prescriber else None,
        medication_id=prescription.medication_id,
        medication_name=prescription.medication.name if prescription.medication else None,
        dosage_value=prescription.dosage_value,
        dosage_unit=prescription.dosage_unit,
        frequency=prescription.frequency,
        route=prescription.route,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        status=prescription.status,
        validation_status=prescription.validation_status,
        validated_by=prescription.validated_by,
        validator_name=prescription.validator.name if prescription.validator else None,
        validation_notes=prescription.validation_notes,
        interactions_checked=prescription.interactions_checked,
        override_justification=prescription.override_justification,
        created_at=prescription.created_at,
    )


@router.post("/{prescription_id}/validate", response_model=PrescriptionResponse)
async def validate_prescription_by_id(
    prescription_id: int,
    data: PrescriptionValidate,
    db: DbSession,
    current_user: User = Depends(require_pharmacien),
):
    """Validate or reject a prescription (pharmacist only)."""
    prescription = await validate_prescription(db, prescription_id, data, current_user)
    return PrescriptionResponse(
        id=prescription.id,
        patient_ipp=prescription.patient_ipp,
        patient_name=prescription.patient_name,
        prescriber_id=prescription.prescriber_id,
        prescriber_name=prescription.prescriber.name if prescription.prescriber else None,
        medication_id=prescription.medication_id,
        medication_name=prescription.medication.name if prescription.medication else None,
        dosage_value=prescription.dosage_value,
        dosage_unit=prescription.dosage_unit,
        frequency=prescription.frequency,
        route=prescription.route,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        status=prescription.status,
        validation_status=prescription.validation_status,
        validated_by=prescription.validated_by,
        validator_name=prescription.validator.name if prescription.validator else None,
        validation_notes=prescription.validation_notes,
        interactions_checked=prescription.interactions_checked,
        override_justification=prescription.override_justification,
        created_at=prescription.created_at,
    )
