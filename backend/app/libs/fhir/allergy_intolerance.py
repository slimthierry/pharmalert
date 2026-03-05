"""
FHIR R4 AllergyIntolerance resource endpoint.
Maps internal PatientAllergy model to/from FHIR AllergyIntolerance.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.models.allergy_models import (
    AllergenType,
    AllergySeverity,
    PatientAllergy,
    ReactionType,
)
from app.schemas.fhir_schemas import (
    FHIRAllergyIntolerance,
    FHIRBundle,
    FHIRBundleEntry,
    FHIRCodeableConcept,
    FHIRCoding,
    FHIRReaction,
    FHIRReference,
)

router = APIRouter()

CATEGORY_MAP = {
    AllergenType.MEDICATION: "medication",
    AllergenType.FOOD: "food",
    AllergenType.ENVIRONMENTAL: "environment",
}

CRITICALITY_MAP = {
    AllergySeverity.MILD: "low",
    AllergySeverity.MODERATE: "low",
    AllergySeverity.SEVERE: "high",
    AllergySeverity.LIFE_THREATENING: "high",
}

SEVERITY_MAP = {
    AllergySeverity.MILD: "mild",
    AllergySeverity.MODERATE: "moderate",
    AllergySeverity.SEVERE: "severe",
    AllergySeverity.LIFE_THREATENING: "severe",
}


def allergy_to_fhir(allergy: PatientAllergy) -> FHIRAllergyIntolerance:
    """Convert an internal PatientAllergy to a FHIR AllergyIntolerance."""
    code_codings = []
    if allergy.atc_code:
        code_codings.append(
            FHIRCoding(
                system="http://www.whocc.no/atc",
                code=allergy.atc_code,
                display=allergy.allergen_name,
            )
        )

    clinical_status = FHIRCodeableConcept(
        coding=[
            FHIRCoding(
                system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                code="active" if allergy.confirmed else "unconfirmed",
            )
        ]
    )

    verification_status = FHIRCodeableConcept(
        coding=[
            FHIRCoding(
                system="http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                code="confirmed" if allergy.confirmed else "unconfirmed",
            )
        ]
    )

    reaction_manifestation = FHIRCodeableConcept(text=allergy.reaction_type.value)
    reaction = FHIRReaction(
        manifestation=[reaction_manifestation],
        severity=SEVERITY_MAP.get(allergy.severity, "moderate"),
    )

    return FHIRAllergyIntolerance(
        id=str(allergy.id),
        clinicalStatus=clinical_status,
        verificationStatus=verification_status,
        type="allergy",
        category=[CATEGORY_MAP.get(allergy.allergen_type, "medication")],
        criticality=CRITICALITY_MAP.get(allergy.severity, "low"),
        code=FHIRCodeableConcept(
            coding=code_codings if code_codings else None,
            text=allergy.allergen_name,
        ),
        patient=FHIRReference(reference=f"Patient/{allergy.patient_ipp}"),
        recorder=FHIRReference(reference=f"Practitioner/{allergy.reported_by}")
        if allergy.reported_by
        else None,
        reaction=[reaction],
        recordedDate=allergy.created_at,
    )


@router.get("/", response_model=FHIRBundle)
async def search_allergy_intolerances(
    db: DbSession,
    current_user: CurrentUser,
    patient: Optional[str] = None,
    category: Optional[str] = None,
    _count: int = 50,
    _offset: int = 0,
):
    """FHIR search for AllergyIntolerance resources."""
    query = select(PatientAllergy)

    if patient:
        query = query.where(PatientAllergy.patient_ipp == patient)
    if category:
        reverse_map = {v: k for k, v in CATEGORY_MAP.items()}
        internal_type = reverse_map.get(category)
        if internal_type:
            query = query.where(PatientAllergy.allergen_type == internal_type)

    result = await db.execute(query.offset(_offset).limit(_count))
    allergies = result.scalars().all()

    entries = [
        FHIRBundleEntry(
            resource=allergy_to_fhir(a).model_dump(),
            fullUrl=f"AllergyIntolerance/{a.id}",
        )
        for a in allergies
    ]

    return FHIRBundle(type="searchset", total=len(entries), entry=entries)


@router.get("/{resource_id}", response_model=FHIRAllergyIntolerance)
async def read_allergy_intolerance(
    resource_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """FHIR read for a specific AllergyIntolerance resource."""
    result = await db.execute(
        select(PatientAllergy).where(PatientAllergy.id == resource_id)
    )
    allergy = result.scalar_one_or_none()

    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AllergyIntolerance not found",
        )

    return allergy_to_fhir(allergy)
