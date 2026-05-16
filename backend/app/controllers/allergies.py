from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_clinical
from app.models.allergy_models import AllergenType
from app.models.user_models import User
from app.schemas.allergy_schemas import (
    AllergyCreate,
    AllergyListResponse,
    AllergyResponse,
    AllergyUpdate,
)
from app.services.allergy_service import (
    create_allergy,
    delete_allergy,
    get_allergy,
    get_patient_allergies,
    list_allergies,
    update_allergy,
)

router = APIRouter()


@router.get("/", response_model=AllergyListResponse)
async def get_allergies(
    db: DbSession,
    current_user: CurrentUser,
    patient_ipp: Optional[str] = None,
    allergen_type: Optional[AllergenType] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List allergies with optional filters."""
    allergies, total = await list_allergies(
        db, patient_ipp=patient_ipp, allergen_type=allergen_type, skip=skip, limit=limit
    )
    return AllergyListResponse(
        items=[AllergyResponse.model_validate(a) for a in allergies],
        total=total,
    )


@router.get("/patient/{patient_ipp}", response_model=list[AllergyResponse])
async def get_patient_allergy_list(
    patient_ipp: str, db: DbSession, current_user: CurrentUser
):
    """Get all allergies for a specific patient."""
    allergies = await get_patient_allergies(db, patient_ipp)
    return [AllergyResponse.model_validate(a) for a in allergies]


@router.get("/{allergy_id}", response_model=AllergyResponse)
async def get_allergy_by_id(
    allergy_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific allergy by ID."""
    allergy = await get_allergy(db, allergy_id)
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergie non trouvee",
        )
    return AllergyResponse.model_validate(allergy)


@router.post("/", response_model=AllergyResponse, status_code=status.HTTP_201_CREATED)
async def create_new_allergy(
    data: AllergyCreate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Create a new patient allergy (clinical staff only)."""
    allergy = await create_allergy(db, data, reported_by=current_user.id)
    return AllergyResponse.model_validate(allergy)


@router.put("/{allergy_id}", response_model=AllergyResponse)
async def update_allergy_by_id(
    allergy_id: int,
    data: AllergyUpdate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Update an allergy record (clinical staff only)."""
    allergy = await update_allergy(db, allergy_id, data)
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergie non trouvee",
        )
    return AllergyResponse.model_validate(allergy)


@router.delete("/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergy_by_id(
    allergy_id: int,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Delete an allergy record (clinical staff only)."""
    deleted = await delete_allergy(db, allergy_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergie non trouvee",
        )
