from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.models.adverse_event_models import AdverseEventSeverity, AdverseEventStatus
from app.schemas.adverse_event_schemas import (
    AdverseEventCreate,
    AdverseEventListResponse,
    AdverseEventResponse,
    AdverseEventStats,
    AdverseEventUpdate,
)
from app.services.adverse_event_service import (
    create_adverse_event,
    get_adverse_event,
    get_adverse_event_stats,
    list_adverse_events,
    update_adverse_event,
)

router = APIRouter()


@router.get("/", response_model=AdverseEventListResponse)
async def get_adverse_events(
    db: DbSession,
    current_user: CurrentUser,
    patient_ipp: Optional[str] = None,
    severity: Optional[AdverseEventSeverity] = None,
    event_status: Optional[AdverseEventStatus] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List adverse events with optional filters."""
    events, total = await list_adverse_events(
        db,
        patient_ipp=patient_ipp,
        severity=severity,
        status=event_status,
        skip=skip,
        limit=limit,
    )

    responses = []
    for e in events:
        responses.append(
            AdverseEventResponse(
                id=e.id,
                patient_ipp=e.patient_ipp,
                medication_id=e.medication_id,
                medication_name=e.medication.name if e.medication else None,
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
        )

    return AdverseEventListResponse(events=responses, total=total)


@router.get("/stats", response_model=AdverseEventStats)
async def get_stats(db: DbSession, current_user: CurrentUser):
    """Get adverse event statistics."""
    return await get_adverse_event_stats(db)


@router.get("/{event_id}", response_model=AdverseEventResponse)
async def get_adverse_event_by_id(
    event_id: int, db: DbSession, current_user: CurrentUser
):
    """Get a specific adverse event by ID."""
    event = await get_adverse_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evenement indesirable non trouve",
        )
    return AdverseEventResponse(
        id=event.id,
        patient_ipp=event.patient_ipp,
        medication_id=event.medication_id,
        medication_name=event.medication.name if event.medication else None,
        prescription_id=event.prescription_id,
        event_type=event.event_type,
        severity=event.severity,
        description=event.description,
        outcome=event.outcome,
        reported_by=event.reported_by,
        reported_at=event.reported_at,
        status=event.status,
        created_at=event.created_at,
    )


@router.post("/", response_model=AdverseEventResponse, status_code=status.HTTP_201_CREATED)
async def create_new_adverse_event(
    data: AdverseEventCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Report a new adverse event (any authenticated user)."""
    event = await create_adverse_event(db, data, current_user)
    return AdverseEventResponse(
        id=event.id,
        patient_ipp=event.patient_ipp,
        medication_id=event.medication_id,
        prescription_id=event.prescription_id,
        event_type=event.event_type,
        severity=event.severity,
        description=event.description,
        outcome=event.outcome,
        reported_by=event.reported_by,
        reported_at=event.reported_at,
        status=event.status,
        created_at=event.created_at,
    )


@router.put("/{event_id}", response_model=AdverseEventResponse)
async def update_adverse_event_by_id(
    event_id: int,
    data: AdverseEventUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update an adverse event (investigation workflow)."""
    event = await update_adverse_event(db, event_id, data, current_user)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evenement indesirable non trouve",
        )
    return AdverseEventResponse(
        id=event.id,
        patient_ipp=event.patient_ipp,
        medication_id=event.medication_id,
        medication_name=event.medication.name if event.medication else None,
        prescription_id=event.prescription_id,
        event_type=event.event_type,
        severity=event.severity,
        description=event.description,
        outcome=event.outcome,
        reported_by=event.reported_by,
        reported_at=event.reported_at,
        status=event.status,
        created_at=event.created_at,
    )
