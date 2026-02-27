from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interaction_models import Interaction, InteractionSeverity
from app.models.medication_models import Medication
from app.schemas.interaction_schemas import (
    InteractionCreate,
    InteractionUpdate,
    InteractionCheckResult,
    InteractionCheckResponse,
    InteractionMatrixEntry,
    InteractionMatrixResponse,
)


async def create_interaction(
    db: AsyncSession, data: InteractionCreate
) -> Interaction:
    """Create a new drug interaction record."""
    interaction = Interaction(
        medication_a_id=data.medication_a_id,
        medication_b_id=data.medication_b_id,
        severity=data.severity,
        mechanism=data.mechanism,
        clinical_effect=data.clinical_effect,
        recommendation=data.recommendation,
        source=data.source,
    )
    db.add(interaction)
    await db.flush()
    await db.refresh(interaction)
    return interaction


async def get_interaction(
    db: AsyncSession, interaction_id: int
) -> Optional[Interaction]:
    """Get an interaction by ID."""
    result = await db.execute(
        select(Interaction)
        .options(selectinload(Interaction.medication_a), selectinload(Interaction.medication_b))
        .where(Interaction.id == interaction_id)
    )
    return result.scalar_one_or_none()


async def update_interaction(
    db: AsyncSession, interaction_id: int, data: InteractionUpdate
) -> Optional[Interaction]:
    """Update an interaction."""
    interaction = await get_interaction(db, interaction_id)
    if not interaction:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)

    await db.flush()
    await db.refresh(interaction)
    return interaction


async def find_interactions_for_medications(
    db: AsyncSession, medication_ids: List[int]
) -> List[InteractionCheckResult]:
    """Find all interactions between a set of medications."""
    if len(medication_ids) < 2:
        return []

    # Query interactions where both medications are in the list
    result = await db.execute(
        select(Interaction)
        .options(selectinload(Interaction.medication_a), selectinload(Interaction.medication_b))
        .where(
            or_(
                (Interaction.medication_a_id.in_(medication_ids))
                & (Interaction.medication_b_id.in_(medication_ids)),
                (Interaction.medication_b_id.in_(medication_ids))
                & (Interaction.medication_a_id.in_(medication_ids)),
            )
        )
    )
    interactions = result.scalars().all()

    results = []
    for interaction in interactions:
        results.append(
            InteractionCheckResult(
                medication_a_id=interaction.medication_a_id,
                medication_a_name=interaction.medication_a.name,
                medication_b_id=interaction.medication_b_id,
                medication_b_name=interaction.medication_b.name,
                severity=interaction.severity,
                clinical_effect=interaction.clinical_effect,
                recommendation=interaction.recommendation,
            )
        )

    return results


async def check_interactions(
    db: AsyncSession, medication_ids: List[int], patient_ipp: Optional[str] = None
) -> InteractionCheckResponse:
    """Check interactions between medications and optionally check allergies."""
    interactions = await find_interactions_for_medications(db, medication_ids)

    has_contraindicated = any(
        i.severity == InteractionSeverity.CONTRAINDICATED for i in interactions
    )
    has_major = any(
        i.severity == InteractionSeverity.MAJOR for i in interactions
    )

    allergy_warnings = []
    if patient_ipp:
        from app.services.allergy_service import check_medication_allergies
        allergy_warnings = await check_medication_allergies(
            db, patient_ipp, medication_ids
        )

    return InteractionCheckResponse(
        interactions=interactions,
        has_contraindicated=has_contraindicated,
        has_major=has_major,
        allergy_warnings=allergy_warnings,
    )


async def get_interaction_matrix(
    db: AsyncSession, medication_ids: List[int]
) -> InteractionMatrixResponse:
    """Get an interaction matrix for a set of medications."""
    # Get medication details
    result = await db.execute(
        select(Medication).where(Medication.id.in_(medication_ids))
    )
    medications = result.scalars().all()
    med_list = [{"id": m.id, "name": m.name, "atc_code": m.atc_code} for m in medications]

    # Get all interactions between these medications
    result = await db.execute(
        select(Interaction).where(
            (Interaction.medication_a_id.in_(medication_ids))
            & (Interaction.medication_b_id.in_(medication_ids))
        )
    )
    interactions = result.scalars().all()

    matrix = []
    for interaction in interactions:
        matrix.append(
            InteractionMatrixEntry(
                medication_a_id=interaction.medication_a_id,
                medication_b_id=interaction.medication_b_id,
                severity=interaction.severity,
            )
        )

    return InteractionMatrixResponse(medications=med_list, matrix=matrix)


async def list_interactions(
    db: AsyncSession,
    severity: Optional[InteractionSeverity] = None,
    medication_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Interaction], int]:
    """List interactions with optional filters."""
    query = select(Interaction).options(
        selectinload(Interaction.medication_a),
        selectinload(Interaction.medication_b),
    )

    if severity:
        query = query.where(Interaction.severity == severity)

    if medication_id:
        query = query.where(
            or_(
                Interaction.medication_a_id == medication_id,
                Interaction.medication_b_id == medication_id,
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(skip).limit(limit).order_by(Interaction.id))
    interactions = list(result.scalars().all())

    return interactions, total
