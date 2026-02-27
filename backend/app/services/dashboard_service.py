from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.administration_models import Administration, AdministrationStatus
from app.models.adverse_event_models import AdverseEvent
from app.models.interaction_models import Interaction, InteractionSeverity
from app.models.prescription_models import (
    Prescription,
    PrescriptionStatus,
    ValidationStatus,
)
from app.schemas.dashboard_schemas import DashboardAlerts, DashboardResponse, DashboardStats


async def get_dashboard_data(db: AsyncSession) -> DashboardResponse:
    """Get dashboard statistics and alerts."""
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Pending validations count
    pending_validations = (
        await db.execute(
            select(func.count()).select_from(
                select(Prescription)
                .where(
                    Prescription.validation_status == ValidationStatus.PENDING,
                    Prescription.status == PrescriptionStatus.ACTIVE,
                )
                .subquery()
            )
        )
    ).scalar()

    # Critical interactions count (contraindicated)
    critical_interactions = (
        await db.execute(
            select(func.count()).select_from(
                select(Interaction)
                .where(Interaction.severity == InteractionSeverity.CONTRAINDICATED)
                .subquery()
            )
        )
    ).scalar()

    # Missed doses today
    missed_doses_today = (
        await db.execute(
            select(func.count()).select_from(
                select(Administration)
                .where(
                    Administration.status == AdministrationStatus.MISSED,
                    Administration.scheduled_at.between(start_of_day, end_of_day),
                )
                .subquery()
            )
        )
    ).scalar()

    # Administration compliance rate (today)
    total_today = (
        await db.execute(
            select(func.count()).select_from(
                select(Administration)
                .where(Administration.scheduled_at.between(start_of_day, end_of_day))
                .subquery()
            )
        )
    ).scalar()

    given_today = (
        await db.execute(
            select(func.count()).select_from(
                select(Administration)
                .where(
                    Administration.status == AdministrationStatus.GIVEN,
                    Administration.scheduled_at.between(start_of_day, end_of_day),
                )
                .subquery()
            )
        )
    ).scalar()

    compliance_rate = (
        round((given_today / total_today) * 100, 1) if total_today > 0 else 100.0
    )

    # Total active prescriptions
    total_active = (
        await db.execute(
            select(func.count()).select_from(
                select(Prescription)
                .where(Prescription.status == PrescriptionStatus.ACTIVE)
                .subquery()
            )
        )
    ).scalar()

    # Total unique patients
    total_patients = (
        await db.execute(
            select(func.count(func.distinct(Prescription.patient_ipp)))
            .where(Prescription.status == PrescriptionStatus.ACTIVE)
        )
    ).scalar()

    stats = DashboardStats(
        pending_validations=pending_validations or 0,
        critical_interactions=critical_interactions or 0,
        missed_doses_today=missed_doses_today or 0,
        compliance_rate=compliance_rate,
        total_active_prescriptions=total_active or 0,
        total_patients=total_patients or 0,
    )

    # Recent adverse events (last 10)
    recent_events_result = await db.execute(
        select(AdverseEvent)
        .order_by(AdverseEvent.reported_at.desc())
        .limit(10)
    )
    recent_events = recent_events_result.scalars().all()

    from app.schemas.adverse_event_schemas import AdverseEventResponse
    adverse_event_responses = [
        AdverseEventResponse(
            id=e.id,
            patient_ipp=e.patient_ipp,
            medication_id=e.medication_id,
            prescription_id=e.prescription_id,
            event_type=e.event_type,
            severity=e.severity,
            description=e.description,
            outcome=e.outcome,
            reported_by=e.reported_by,
            reported_at=e.reported_at,
            status=e.status,
            created_at=e.created_at,
        )
        for e in recent_events
    ]

    alerts = DashboardAlerts(
        critical_interactions=[],
        recent_adverse_events=adverse_event_responses,
    )

    return DashboardResponse(stats=stats, alerts=alerts)
