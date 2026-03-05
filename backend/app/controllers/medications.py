from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_clinical
from app.models.user_models import User
from app.schemas.medication_schemas import (
    MedicationCreate,
    MedicationListResponse,
    MedicationResponse,
    MedicationUpdate,
)
from app.services.medication_service import (
    create_medication,
    delete_medication,
    get_medication,
    list_medications,
    update_medication,
)

router = APIRouter()


@router.get("/", response_model=MedicationListResponse)
async def get_medications(
    db: DbSession,
    current_user: CurrentUser,
    search: Optional[str] = None,
    atc_code: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List medications with optional search and ATC filter."""
    medications, total = await list_medications(
        db, search=search, atc_code=atc_code, skip=skip, limit=limit
    )
    return MedicationListResponse(
        medications=[MedicationResponse.model_validate(m) for m in medications],
        total=total,
    )


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication_by_id(
    medication_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific medication by ID."""
    medication = await get_medication(db, medication_id)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament non trouve",
        )
    return MedicationResponse.model_validate(medication)


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_medication(
    data: MedicationCreate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Create a new medication (clinical staff only)."""
    medication = await create_medication(db, data)
    return MedicationResponse.model_validate(medication)


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication_by_id(
    medication_id: int,
    data: MedicationUpdate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Update a medication (clinical staff only)."""
    medication = await update_medication(db, medication_id, data)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament non trouve",
        )
    return MedicationResponse.model_validate(medication)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication_by_id(
    medication_id: int,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Delete a medication (clinical staff only)."""
    deleted = await delete_medication(db, medication_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament non trouve",
        )
