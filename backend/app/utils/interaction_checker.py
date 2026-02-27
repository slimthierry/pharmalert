"""
Core interaction checking logic.
Provides functions to check medication interactions and patient allergies
when creating or modifying prescriptions.
"""

from typing import List, Optional, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.allergy_models import AllergenType, PatientAllergy
from app.models.interaction_models import Interaction, InteractionSeverity
from app.models.medication_models import Medication
from app.models.prescription_models import Prescription, PrescriptionStatus


class InteractionCheckResult:
    """Result of an interaction check."""

    def __init__(
        self,
        medication_a: Medication,
        medication_b: Medication,
        severity: InteractionSeverity,
        clinical_effect: str,
        recommendation: str,
        mechanism: Optional[str] = None,
    ):
        self.medication_a = medication_a
        self.medication_b = medication_b
        self.severity = severity
        self.clinical_effect = clinical_effect
        self.recommendation = recommendation
        self.mechanism = mechanism


class AllergyWarning:
    """Warning about a potential allergy conflict."""

    def __init__(
        self,
        medication: Medication,
        allergy: PatientAllergy,
        message: str,
    ):
        self.medication = medication
        self.allergy = allergy
        self.message = message


async def check_prescription_interactions(
    db: AsyncSession,
    patient_ipp: str,
    new_medication_id: int,
) -> Tuple[List[InteractionCheckResult], List[AllergyWarning]]:
    """
    CRITICAL: Check all interactions for a new prescription.

    1. Get all active prescriptions for the patient
    2. Check the new medication against every active medication
    3. Check against patient allergies
    4. Return interaction results and allergy warnings
    """
    interactions = []
    allergy_warnings = []

    # Get the new medication
    new_med_result = await db.execute(
        select(Medication).where(Medication.id == new_medication_id)
    )
    new_medication = new_med_result.scalar_one_or_none()
    if not new_medication:
        return interactions, allergy_warnings

    # Get all active prescriptions for this patient
    active_result = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.medication))
        .where(
            Prescription.patient_ipp == patient_ipp,
            Prescription.status == PrescriptionStatus.ACTIVE,
        )
    )
    active_prescriptions = active_result.scalars().all()

    # Get all medication IDs to check
    active_medication_ids = [p.medication_id for p in active_prescriptions]

    if active_medication_ids:
        # Find interactions between the new medication and all active ones
        interaction_result = await db.execute(
            select(Interaction)
            .options(
                selectinload(Interaction.medication_a),
                selectinload(Interaction.medication_b),
            )
            .where(
                or_(
                    (Interaction.medication_a_id == new_medication_id)
                    & (Interaction.medication_b_id.in_(active_medication_ids)),
                    (Interaction.medication_b_id == new_medication_id)
                    & (Interaction.medication_a_id.in_(active_medication_ids)),
                )
            )
        )
        found_interactions = interaction_result.scalars().all()

        for interaction in found_interactions:
            interactions.append(
                InteractionCheckResult(
                    medication_a=interaction.medication_a,
                    medication_b=interaction.medication_b,
                    severity=interaction.severity,
                    clinical_effect=interaction.clinical_effect,
                    recommendation=interaction.recommendation,
                    mechanism=interaction.mechanism,
                )
            )

    # Check allergies
    allergy_result = await db.execute(
        select(PatientAllergy).where(
            PatientAllergy.patient_ipp == patient_ipp,
            PatientAllergy.allergen_type == AllergenType.MEDICATION,
        )
    )
    patient_allergies = allergy_result.scalars().all()

    for allergy in patient_allergies:
        # Check by ATC code prefix match
        if (
            allergy.atc_code
            and new_medication.atc_code
            and new_medication.atc_code.startswith(allergy.atc_code)
        ):
            allergy_warnings.append(
                AllergyWarning(
                    medication=new_medication,
                    allergy=allergy,
                    message=(
                        f"ALLERGIE DETECTEE: {new_medication.name} "
                        f"(ATC: {new_medication.atc_code}) correspond a l'allergie "
                        f"connue: {allergy.allergen_name} "
                        f"(severite: {allergy.severity.value})"
                    ),
                )
            )
        # Check by name match (DCI or brand name)
        elif (
            allergy.allergen_name.lower() in new_medication.name.lower()
            or allergy.allergen_name.lower() in new_medication.dci.lower()
        ):
            allergy_warnings.append(
                AllergyWarning(
                    medication=new_medication,
                    allergy=allergy,
                    message=(
                        f"ALLERGIE DETECTEE: {new_medication.name} "
                        f"(DCI: {new_medication.dci}) correspond a l'allergie "
                        f"connue: {allergy.allergen_name} "
                        f"(severite: {allergy.severity.value})"
                    ),
                )
            )

    return interactions, allergy_warnings


def has_blocking_interaction(interactions: List[InteractionCheckResult]) -> bool:
    """Check if any interaction is contraindicated (blocking)."""
    return any(
        i.severity == InteractionSeverity.CONTRAINDICATED for i in interactions
    )


def has_major_interaction(interactions: List[InteractionCheckResult]) -> bool:
    """Check if any interaction is major (alert required)."""
    return any(
        i.severity == InteractionSeverity.MAJOR for i in interactions
    )


def get_severity_level(interactions: List[InteractionCheckResult]) -> Optional[str]:
    """Get the highest severity level from a list of interactions."""
    if not interactions:
        return None

    severity_order = [
        InteractionSeverity.CONTRAINDICATED,
        InteractionSeverity.MAJOR,
        InteractionSeverity.MODERATE,
        InteractionSeverity.MINOR,
    ]

    for severity in severity_order:
        if any(i.severity == severity for i in interactions):
            return severity.value

    return None
