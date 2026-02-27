"""
Background tasks for periodic interaction checks.
Rechecks active prescriptions for any new interactions added to the database.
"""

import logging
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config.database import AsyncSessionLocal
from app.models.prescription_models import Prescription, PrescriptionStatus
from app.services.interaction_service import find_interactions_for_medications
from app.services.webhook_service import send_webhook

logger = logging.getLogger(__name__)


async def recheck_active_prescriptions() -> None:
    """
    Periodically recheck all active prescriptions for interactions.
    Useful when new interactions are added to the database.
    """
    async with AsyncSessionLocal() as db:
        # Group active prescriptions by patient
        result = await db.execute(
            select(Prescription)
            .options(selectinload(Prescription.medication))
            .where(Prescription.status == PrescriptionStatus.ACTIVE)
        )
        prescriptions = result.scalars().all()

        # Group by patient
        patient_prescriptions: Dict[str, List[Prescription]] = {}
        for p in prescriptions:
            if p.patient_ipp not in patient_prescriptions:
                patient_prescriptions[p.patient_ipp] = []
            patient_prescriptions[p.patient_ipp].append(p)

        # Check interactions per patient
        for patient_ipp, patient_rxs in patient_prescriptions.items():
            if len(patient_rxs) < 2:
                continue

            medication_ids = [p.medication_id for p in patient_rxs]
            interactions = await find_interactions_for_medications(db, medication_ids)

            critical = [
                i for i in interactions
                if i.severity.value in ("contraindicated", "major")
            ]

            if critical:
                logger.warning(
                    f"Critical interactions found for patient {patient_ipp}: "
                    f"{len(critical)} interactions"
                )
                await send_webhook(
                    event_type="critical_interaction",
                    payload={
                        "patient_ipp": patient_ipp,
                        "interactions": [i.model_dump() for i in critical],
                        "source": "periodic_recheck",
                    },
                )

        logger.info(
            f"Interaction recheck completed for {len(patient_prescriptions)} patients"
        )
