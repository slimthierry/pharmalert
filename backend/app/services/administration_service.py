from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit
from app.models.administration_models import Administration, AdministrationStatus
from app.models.prescription_models import Prescription
from app.models.user_models import User
from app.schemas.administration_schemas import (
    AdministrationCreate,
    AdministrationRecord,
)
from app.services.webhook_service import send_webhook


async def create_administration(
    db: AsyncSession, data: AdministrationCreate
) -> Administration:
    """Schedule a new administration."""
    administration = Administration(
        prescription_id=data.prescription_id,
        scheduled_at=data.scheduled_at,
        patient_ipp=data.patient_ipp,
        status=AdministrationStatus.MISSED,  # Default until recorded
    )
    db.add(administration)
    await db.flush()
    await db.refresh(administration)
    return administration


async def record_administration(
    db: AsyncSession,
    administration_id: int,
    record: AdministrationRecord,
    nurse: User,
) -> Optional[Administration]:
    """Record an administration (nurse marks as given/refused/missed/delayed)."""
    result = await db.execute(
        select(Administration)
        .options(selectinload(Administration.prescription))
        .where(Administration.id == administration_id)
    )
    administration = result.scalar_one_or_none()

    if not administration:
        return None

    administration.nurse_id = nurse.id
    administration.status = record.status
    administration.dose_given = record.dose_given
    administration.notes = record.notes
    administration.vital_signs = record.vital_signs

    if record.status == AdministrationStatus.GIVEN:
        administration.administered_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(administration)

    # Audit log
    await log_audit(
        db,
        user_id=nurse.id,
        action=f"record_administration_{record.status.value}",
        entity_type="administration",
        entity_id=str(administration_id),
        details={
            "status": record.status.value,
            "dose_given": record.dose_given,
            "patient_ipp": administration.patient_ipp,
        },
    )

    # Send webhook for missed doses
    if record.status == AdministrationStatus.MISSED:
        await send_webhook(
            event_type="missed_dose",
            payload={
                "administration_id": administration.id,
                "prescription_id": administration.prescription_id,
                "patient_ipp": administration.patient_ipp,
                "scheduled_at": administration.scheduled_at.isoformat(),
            },
        )

    return administration


async def get_administration(
    db: AsyncSession, administration_id: int
) -> Optional[Administration]:
    """Get an administration by ID."""
    result = await db.execute(
        select(Administration)
        .options(
            selectinload(Administration.prescription).selectinload(Prescription.medication),
            selectinload(Administration.nurse),
        )
        .where(Administration.id == administration_id)
    )
    return result.scalar_one_or_none()


async def list_administrations(
    db: AsyncSession,
    patient_ipp: Optional[str] = None,
    nurse_id: Optional[int] = None,
    status: Optional[AdministrationStatus] = None,
    scheduled_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Administration], int]:
    """List administrations with optional filters."""
    query = select(Administration).options(
        selectinload(Administration.prescription).selectinload(Prescription.medication),
        selectinload(Administration.nurse),
    )

    if patient_ipp:
        query = query.where(Administration.patient_ipp == patient_ipp)
    if nurse_id:
        query = query.where(Administration.nurse_id == nurse_id)
    if status:
        query = query.where(Administration.status == status)
    if scheduled_date:
        # Filter by date (same day)
        start_of_day = scheduled_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = scheduled_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.where(
            Administration.scheduled_at.between(start_of_day, end_of_day)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Administration.scheduled_at)
    )
    administrations = list(result.scalars().all())

    return administrations, total


async def get_today_schedule(
    db: AsyncSession, nurse_id: Optional[int] = None
) -> List[Administration]:
    """Get today's administration schedule."""
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    query = (
        select(Administration)
        .options(
            selectinload(Administration.prescription).selectinload(Prescription.medication),
            selectinload(Administration.nurse),
        )
        .where(Administration.scheduled_at.between(start_of_day, end_of_day))
        .order_by(Administration.scheduled_at)
    )

    if nurse_id:
        query = query.where(Administration.nurse_id == nurse_id)

    result = await db.execute(query)
    return list(result.scalars().all())
