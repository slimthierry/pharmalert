from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.rbac import require_clinical
from app.models.interaction_models import InteractionSeverity
from app.models.user_models import User
from app.schemas.interaction_schemas import (
    InteractionCheckRequest,
    InteractionCheckResponse,
    InteractionCreate,
    InteractionListResponse,
    InteractionMatrixResponse,
    InteractionResponse,
    InteractionUpdate,
)
from app.services.interaction_service import (
    check_interactions,
    create_interaction,
    get_interaction,
    get_interaction_matrix,
    list_interactions,
    update_interaction,
)

router = APIRouter()


@router.get("/", response_model=InteractionListResponse)
async def get_interactions(
    db: DbSession,
    current_user: CurrentUser,
    severity: Optional[InteractionSeverity] = None,
    medication_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List drug interactions with optional filters."""
    interactions, total = await list_interactions(
        db, severity=severity, medication_id=medication_id, skip=skip, limit=limit
    )

    responses = []
    for i in interactions:
        responses.append(
            InteractionResponse(
                id=i.id,
                medication_a_id=i.medication_a_id,
                medication_a_name=i.medication_a.name if i.medication_a else None,
                medication_b_id=i.medication_b_id,
                medication_b_name=i.medication_b.name if i.medication_b else None,
                severity=i.severity,
                mechanism=i.mechanism,
                clinical_effect=i.clinical_effect,
                recommendation=i.recommendation,
                source=i.source,
                created_at=i.created_at,
            )
        )

    return InteractionListResponse(interactions=responses, total=total)


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction_by_id(
    interaction_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific interaction by ID."""
    interaction = await get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction non trouvee",
        )
    return InteractionResponse(
        id=interaction.id,
        medication_a_id=interaction.medication_a_id,
        medication_a_name=interaction.medication_a.name if interaction.medication_a else None,
        medication_b_id=interaction.medication_b_id,
        medication_b_name=interaction.medication_b.name if interaction.medication_b else None,
        severity=interaction.severity,
        mechanism=interaction.mechanism,
        clinical_effect=interaction.clinical_effect,
        recommendation=interaction.recommendation,
        source=interaction.source,
        created_at=interaction.created_at,
    )


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_interaction(
    data: InteractionCreate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Create a new drug interaction record (clinical staff only)."""
    interaction = await create_interaction(db, data)
    return InteractionResponse(
        id=interaction.id,
        medication_a_id=interaction.medication_a_id,
        medication_b_id=interaction.medication_b_id,
        severity=interaction.severity,
        mechanism=interaction.mechanism,
        clinical_effect=interaction.clinical_effect,
        recommendation=interaction.recommendation,
        source=interaction.source,
        created_at=interaction.created_at,
    )


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction_by_id(
    interaction_id: int,
    data: InteractionUpdate,
    db: DbSession,
    current_user: User = Depends(require_clinical),
):
    """Update an interaction (clinical staff only)."""
    interaction = await update_interaction(db, interaction_id, data)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction non trouvee",
        )
    return InteractionResponse(
        id=interaction.id,
        medication_a_id=interaction.medication_a_id,
        medication_a_name=interaction.medication_a.name if interaction.medication_a else None,
        medication_b_id=interaction.medication_b_id,
        medication_b_name=interaction.medication_b.name if interaction.medication_b else None,
        severity=interaction.severity,
        mechanism=interaction.mechanism,
        clinical_effect=interaction.clinical_effect,
        recommendation=interaction.recommendation,
        source=interaction.source,
        created_at=interaction.created_at,
    )


@router.post("/check", response_model=InteractionCheckResponse)
async def check_medication_interactions(
    data: InteractionCheckRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Check interactions between a set of medications."""
    return await check_interactions(
        db, data.medication_ids, patient_ipp=data.patient_ipp
    )


@router.post("/matrix", response_model=InteractionMatrixResponse)
async def get_interaction_matrix_view(
    medication_ids: List[int],
    db: DbSession,
    current_user: CurrentUser,
):
    """Get an interaction matrix for a set of medications."""
    return await get_interaction_matrix(db, medication_ids)
