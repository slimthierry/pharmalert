from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.audit import log_audit
from app.models.adverse_event_models import (
    AdverseEvent,
    AdverseEventSeverity,
    AdverseEventStatus,
    AdverseEventType,
)
from app.models.user_models import User
from app.schemas.adverse_event_schemas import (
    AdverseEventCreate,
    AdverseEventStats,
    AdverseEventUpdate,
)
from app.services.webhook_service import send_webhook


async def create_adverse_event(
    db: AsyncSession, data: AdverseEventCreate, reporter: User
) -> AdverseEvent:
    """Report a new adverse event."""
    event = AdverseEvent(
        patient_ipp=data.patient_ipp,
        medication_id=data.medication_id,
        prescription_id=data.prescription_id,
        event_type=data.event_type,
        severity=data.severity,
        description=data.description,
        reported_by=reporter.id,
        reported_at=data.reported_at or datetime.now(timezone.utc),
        status=AdverseEventStatus.REPORTED,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)

    # Audit log
    await log_audit(
        db,
        user_id=reporter.id,
        action="report_adverse_event",
        entity_type="adverse_event",
        entity_id=str(event.id),
        details={
            "patient_ipp": data.patient_ipp,
            "severity": data.severity.value,
            "event_type": data.event_type.value,
        },
    )

    # Send webhook for serious adverse events
    if data.severity in (
        AdverseEventSeverity.SERIOUS,
        AdverseEventSeverity.LIFE_THREATENING,
    ):
        await send_webhook(
            event_type="adverse_event",
            payload={
                "event_id": event.id,
                "patient_ipp": data.patient_ipp,
                "severity": data.severity.value,
                "description": data.description,
            },
        )

    return event


async def get_adverse_event(
    db: AsyncSession, event_id: int
) -> Optional[AdverseEvent]:
    """Get an adverse event by ID."""
    result = await db.execute(
        select(AdverseEvent)
        .options(
            selectinload(AdverseEvent.medication),
            selectinload(AdverseEvent.prescription),
        )
        .where(AdverseEvent.id == event_id)
    )
    return result.scalar_one_or_none()


async def update_adverse_event(
    db: AsyncSession, event_id: int, data: AdverseEventUpdate, user: User
) -> Optional[AdverseEvent]:
    """Update an adverse event (investigation workflow)."""
    event = await get_adverse_event(db, event_id)
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await db.flush()
    await db.refresh(event)

    await log_audit(
        db,
        user_id=user.id,
        action="update_adverse_event",
        entity_type="adverse_event",
        entity_id=str(event_id),
        details=update_data,
    )

    return event


async def list_adverse_events(
    db: AsyncSession,
    patient_ipp: Optional[str] = None,
    severity: Optional[AdverseEventSeverity] = None,
    status: Optional[AdverseEventStatus] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[AdverseEvent], int]:
    """List adverse events with optional filters."""
    query = select(AdverseEvent).options(
        selectinload(AdverseEvent.medication),
    )

    if patient_ipp:
        query = query.where(AdverseEvent.patient_ipp == patient_ipp)
    if severity:
        query = query.where(AdverseEvent.severity == severity)
    if status:
        query = query.where(AdverseEvent.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(
        query.offset(skip).limit(limit).order_by(AdverseEvent.reported_at.desc())
    )
    events = list(result.scalars().all())

    return events, total


async def get_adverse_event_stats(db: AsyncSession) -> AdverseEventStats:
    """Get adverse event statistics."""
    # Total count
    total = (
        await db.execute(select(func.count()).select_from(AdverseEvent))
    ).scalar()

    # By severity
    severity_result = await db.execute(
        select(AdverseEvent.severity, func.count())
        .group_by(AdverseEvent.severity)
    )
    by_severity = {row[0].value: row[1] for row in severity_result.all()}

    # By type
    type_result = await db.execute(
        select(AdverseEvent.event_type, func.count())
        .group_by(AdverseEvent.event_type)
    )
    by_type = {row[0].value: row[1] for row in type_result.all()}

    # By status
    status_result = await db.execute(
        select(AdverseEvent.status, func.count())
        .group_by(AdverseEvent.status)
    )
    by_status = {row[0].value: row[1] for row in status_result.all()}

    return AdverseEventStats(
        total=total,
        by_severity=by_severity,
        by_type=by_type,
        by_status=by_status,
    )
