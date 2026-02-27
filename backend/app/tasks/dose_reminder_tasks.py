"""
Background tasks for dose reminders.
Checks for upcoming administrations and sends alerts for missed doses.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.config.database import AsyncSessionLocal
from app.models.administration_models import Administration, AdministrationStatus
from app.services.webhook_service import send_webhook

logger = logging.getLogger(__name__)


async def check_missed_doses() -> None:
    """
    Check for doses that were scheduled but not yet administered.
    Sends a webhook alert for each missed dose.
    """
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(minutes=30)  # 30 min grace period

        result = await db.execute(
            select(Administration).where(
                Administration.scheduled_at < threshold,
                Administration.status == AdministrationStatus.MISSED,
                Administration.administered_at.is_(None),
            )
        )
        missed_doses = result.scalars().all()

        for dose in missed_doses:
            logger.warning(
                f"Missed dose detected: administration_id={dose.id}, "
                f"patient_ipp={dose.patient_ipp}, "
                f"scheduled_at={dose.scheduled_at}"
            )
            await send_webhook(
                event_type="missed_dose",
                payload={
                    "administration_id": dose.id,
                    "prescription_id": dose.prescription_id,
                    "patient_ipp": dose.patient_ipp,
                    "scheduled_at": dose.scheduled_at.isoformat(),
                },
            )

        logger.info(f"Missed dose check completed: {len(missed_doses)} missed doses found")


async def check_upcoming_doses() -> None:
    """
    Check for doses scheduled in the next 30 minutes.
    Can be used to send reminders to nursing staff.
    """
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        upcoming_window = now + timedelta(minutes=30)

        result = await db.execute(
            select(Administration).where(
                Administration.scheduled_at.between(now, upcoming_window),
                Administration.administered_at.is_(None),
            )
        )
        upcoming_doses = result.scalars().all()

        logger.info(
            f"Upcoming dose check: {len(upcoming_doses)} doses in the next 30 minutes"
        )
