from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.audit import log_audit
from app.auth.exceptions import (
    AllergyConflictException,
    InteractionContraindicatedException,
    NotFoundException,
)
from app.models.prescription_models import (
    Prescription,
    PrescriptionStatus,
    ValidationStatus,
)
from app.models.user_models import User
from app.schemas.prescription_schemas import (
    PrescriptionCreate,
    PrescriptionCreateResponse,
    PrescriptionResponse,
    PrescriptionUpdate,
    PrescriptionValidate,
)
from app.services.interaction_service import check_interactions
from app.services.webhook_service import send_webhook


async def create_prescription(
    db: AsyncSession, data: PrescriptionCreate, prescriber: User
) -> PrescriptionCreateResponse:
    """
    Create a new prescription with automatic interaction checking.
    This is the CRITICAL path - must check all interactions.
    """
    # Get all active prescriptions for this patient
    active_result = await db.execute(
        select(Prescription)
        .where(
            Prescription.patient_ipp == data.patient_ipp,
            Prescription.status == PrescriptionStatus.ACTIVE,
        )
    )
    active_prescriptions = active_result.scalars().all()

    # Build list of all medication IDs (existing + new)
    medication_ids = [p.medication_id for p in active_prescriptions]
    medication_ids.append(data.medication_id)

    # Check interactions
    interaction_check = await check_interactions(
        db, medication_ids, patient_ipp=data.patient_ipp
    )

    # Block if contraindicated (unless doctor provides justification)
    if interaction_check.has_contraindicated and not data.override_justification:
        contraindicated = [
            i for i in interaction_check.interactions
            if i.severity.value == "contraindicated"
        ]
        details = "; ".join([
            f"{i.medication_a_name} + {i.medication_b_name}: {i.clinical_effect}"
            for i in contraindicated
        ])
        raise InteractionContraindicatedException(
            detail=f"Interaction contre-indiquee detectee: {details}. "
            "Fournir une justification (override_justification) pour passer outre."
        )

    # Check allergy warnings
    if interaction_check.allergy_warnings:
        # Don't block but include warnings
        pass

    # Create the prescription
    prescription = Prescription(
        patient_ipp=data.patient_ipp,
        patient_name=data.patient_name,
        prescriber_id=prescriber.id,
        medication_id=data.medication_id,
        dosage_value=data.dosage_value,
        dosage_unit=data.dosage_unit,
        frequency=data.frequency,
        route=data.route,
        start_date=data.start_date,
        end_date=data.end_date,
        interactions_checked=True,
        override_justification=data.override_justification,
    )
    db.add(prescription)
    await db.flush()
    await db.refresh(prescription)

    # Load relationships for response
    await db.refresh(prescription, ["prescriber", "medication"])

    # Audit log
    await log_audit(
        db,
        user_id=prescriber.id,
        action="create_prescription",
        entity_type="prescription",
        entity_id=str(prescription.id),
        details={
            "patient_ipp": data.patient_ipp,
            "medication_id": data.medication_id,
            "interactions_found": len(interaction_check.interactions),
            "has_contraindicated": interaction_check.has_contraindicated,
            "override": bool(data.override_justification),
        },
    )

    # Send webhook for critical interactions
    if interaction_check.has_contraindicated or interaction_check.has_major:
        await send_webhook(
            event_type="critical_interaction",
            payload={
                "prescription_id": prescription.id,
                "patient_ipp": data.patient_ipp,
                "interactions": [i.model_dump() for i in interaction_check.interactions],
            },
        )

    response_prescription = PrescriptionResponse(
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
        validation_notes=prescription.validation_notes,
        interactions_checked=prescription.interactions_checked,
        override_justification=prescription.override_justification,
        created_at=prescription.created_at,
    )

    return PrescriptionCreateResponse(
        prescription=response_prescription,
        interactions=[i for i in interaction_check.interactions],
        allergy_warnings=interaction_check.allergy_warnings,
    )


async def validate_prescription(
    db: AsyncSession,
    prescription_id: int,
    validation: PrescriptionValidate,
    pharmacist: User,
) -> Optional[Prescription]:
    """Validate or reject a prescription (pharmacist only)."""
    result = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.prescriber), selectinload(Prescription.medication))
        .where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()

    if not prescription:
        raise NotFoundException("Prescription", str(prescription_id))

    prescription.validation_status = validation.validation_status
    prescription.validated_by = pharmacist.id
    prescription.validation_notes = validation.validation_notes

    await db.flush()
    await db.refresh(prescription)

    await log_audit(
        db,
        user_id=pharmacist.id,
        action=f"validate_prescription_{validation.validation_status.value}",
        entity_type="prescription",
        entity_id=str(prescription_id),
        details={
            "validation_status": validation.validation_status.value,
            "notes": validation.validation_notes,
        },
    )

    return prescription


async def get_prescription(
    db: AsyncSession, prescription_id: int
) -> Optional[Prescription]:
    """Get a prescription by ID with relationships loaded."""
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.prescriber),
            selectinload(Prescription.medication),
            selectinload(Prescription.validator),
        )
        .where(Prescription.id == prescription_id)
    )
    return result.scalar_one_or_none()


async def update_prescription(
    db: AsyncSession, prescription_id: int, data: PrescriptionUpdate
) -> Optional[Prescription]:
    """Update a prescription."""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)

    await db.flush()
    await db.refresh(prescription)
    return prescription


async def list_prescriptions(
    db: AsyncSession,
    patient_ipp: Optional[str] = None,
    status: Optional[PrescriptionStatus] = None,
    validation_status: Optional[ValidationStatus] = None,
    prescriber_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Prescription], int]:
    """List prescriptions with optional filters."""
    query = select(Prescription).options(
        selectinload(Prescription.prescriber),
        selectinload(Prescription.medication),
        selectinload(Prescription.validator),
    )

    if patient_ipp:
        query = query.where(Prescription.patient_ipp == patient_ipp)
    if status:
        query = query.where(Prescription.status == status)
    if validation_status:
        query = query.where(Prescription.validation_status == validation_status)
    if prescriber_id:
        query = query.where(Prescription.prescriber_id == prescriber_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Prescription.created_at.desc())
    )
    prescriptions = list(result.scalars().all())

    return prescriptions, total
