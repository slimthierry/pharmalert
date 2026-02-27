from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allergy_models import AllergenType, PatientAllergy
from app.models.medication_models import Medication
from app.schemas.allergy_schemas import AllergyCreate, AllergyUpdate


async def create_allergy(
    db: AsyncSession, data: AllergyCreate, reported_by: int
) -> PatientAllergy:
    """Create a new patient allergy record."""
    allergy = PatientAllergy(
        patient_ipp=data.patient_ipp,
        allergen_type=data.allergen_type,
        allergen_name=data.allergen_name,
        atc_code=data.atc_code,
        severity=data.severity,
        reaction_type=data.reaction_type,
        confirmed=data.confirmed,
        reported_by=reported_by,
    )
    db.add(allergy)
    await db.flush()
    await db.refresh(allergy)
    return allergy


async def get_allergy(db: AsyncSession, allergy_id: int) -> Optional[PatientAllergy]:
    """Get an allergy by ID."""
    result = await db.execute(
        select(PatientAllergy).where(PatientAllergy.id == allergy_id)
    )
    return result.scalar_one_or_none()


async def update_allergy(
    db: AsyncSession, allergy_id: int, data: AllergyUpdate
) -> Optional[PatientAllergy]:
    """Update an allergy record."""
    allergy = await get_allergy(db, allergy_id)
    if not allergy:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(allergy, field, value)

    await db.flush()
    await db.refresh(allergy)
    return allergy


async def list_allergies(
    db: AsyncSession,
    patient_ipp: Optional[str] = None,
    allergen_type: Optional[AllergenType] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[PatientAllergy], int]:
    """List allergies with optional filters."""
    query = select(PatientAllergy)

    if patient_ipp:
        query = query.where(PatientAllergy.patient_ipp == patient_ipp)
    if allergen_type:
        query = query.where(PatientAllergy.allergen_type == allergen_type)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(PatientAllergy.created_at.desc())
    )
    allergies = list(result.scalars().all())

    return allergies, total


async def get_patient_allergies(
    db: AsyncSession, patient_ipp: str
) -> List[PatientAllergy]:
    """Get all allergies for a specific patient."""
    result = await db.execute(
        select(PatientAllergy)
        .where(PatientAllergy.patient_ipp == patient_ipp)
        .order_by(PatientAllergy.severity.desc())
    )
    return list(result.scalars().all())


async def check_medication_allergies(
    db: AsyncSession, patient_ipp: str, medication_ids: List[int]
) -> List[str]:
    """Check if any medications conflict with patient's known allergies."""
    warnings = []

    # Get patient's medication allergies
    allergies = await db.execute(
        select(PatientAllergy).where(
            PatientAllergy.patient_ipp == patient_ipp,
            PatientAllergy.allergen_type == AllergenType.MEDICATION,
        )
    )
    patient_allergies = allergies.scalars().all()

    if not patient_allergies:
        return warnings

    # Get medications
    meds_result = await db.execute(
        select(Medication).where(Medication.id.in_(medication_ids))
    )
    medications = meds_result.scalars().all()

    for allergy in patient_allergies:
        for medication in medications:
            # Check by ATC code match
            if (
                allergy.atc_code
                and medication.atc_code
                and medication.atc_code.startswith(allergy.atc_code)
            ):
                warnings.append(
                    f"ALLERGIE: {medication.name} (ATC: {medication.atc_code}) - "
                    f"Patient allergique a {allergy.allergen_name} "
                    f"(severite: {allergy.severity.value})"
                )
            # Check by name match
            elif allergy.allergen_name.lower() in medication.name.lower():
                warnings.append(
                    f"ALLERGIE: {medication.name} - "
                    f"Patient allergique a {allergy.allergen_name} "
                    f"(severite: {allergy.severity.value})"
                )
            elif allergy.allergen_name.lower() in medication.dci.lower():
                warnings.append(
                    f"ALLERGIE: {medication.name} (DCI: {medication.dci}) - "
                    f"Patient allergique a {allergy.allergen_name} "
                    f"(severite: {allergy.severity.value})"
                )

    return warnings


async def delete_allergy(db: AsyncSession, allergy_id: int) -> bool:
    """Delete an allergy record."""
    allergy = await get_allergy(db, allergy_id)
    if not allergy:
        return False
    await db.delete(allergy)
    await db.flush()
    return True
