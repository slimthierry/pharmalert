from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medication_models import Medication
from app.schemas.medication_schemas import MedicationCreate, MedicationUpdate


async def create_medication(
    db: AsyncSession, data: MedicationCreate
) -> Medication:
    """Create a new medication."""
    medication = Medication(
        name=data.name,
        dci=data.dci,
        atc_code=data.atc_code,
        form=data.form,
        dosage_unit=data.dosage_unit,
        manufacturer=data.manufacturer,
        contraindications=data.contraindications,
        side_effects=data.side_effects,
    )
    db.add(medication)
    await db.flush()
    await db.refresh(medication)
    return medication


async def get_medication(db: AsyncSession, medication_id: int) -> Optional[Medication]:
    """Get a medication by ID."""
    result = await db.execute(
        select(Medication).where(Medication.id == medication_id)
    )
    return result.scalar_one_or_none()


async def update_medication(
    db: AsyncSession, medication_id: int, data: MedicationUpdate
) -> Optional[Medication]:
    """Update a medication."""
    medication = await get_medication(db, medication_id)
    if not medication:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medication, field, value)

    await db.flush()
    await db.refresh(medication)
    return medication


async def list_medications(
    db: AsyncSession,
    search: Optional[str] = None,
    atc_code: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Medication], int]:
    """List medications with optional search and ATC filter."""
    query = select(Medication)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Medication.name.ilike(search_filter))
            | (Medication.dci.ilike(search_filter))
        )

    if atc_code:
        query = query.where(Medication.atc_code.startswith(atc_code))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Fetch
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Medication.name)
    )
    medications = list(result.scalars().all())

    return medications, total


async def delete_medication(db: AsyncSession, medication_id: int) -> bool:
    """Delete a medication."""
    medication = await get_medication(db, medication_id)
    if not medication:
        return False
    await db.delete(medication)
    await db.flush()
    return True
