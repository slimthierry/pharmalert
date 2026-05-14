"""
Entity management API endpoints.

Handles CRUD for entities, user assignments, and services.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_admin
from app.models.user_models import User
from app.schemas.entity_schemas import (
    EntityCreate, EntityUpdate, EntityResponse, EntityListResponse,
    EntityBriefResponse, EntityUserAssignmentCreate, EntityUserAssignmentUpdate,
    EntityUserAssignmentResponse, UserWithEntitiesResponse,
    EntityServiceCreate, EntityServiceUpdate, EntityServiceResponse,
    EntityServiceListResponse
)
from app.services.entity_service import EntityService

router = APIRouter()


# ========================
# Entity CRUD
# ========================


@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    data: EntityCreate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Create a new entity (admin only)."""
    service = EntityService(db)

    # Check if code already exists
    existing = await service.get_entity_by_code(data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un établissement avec le code '{data.code}' existe déjà"
        )

    entity = await service.create_entity(data, created_by=current_user.id)
    return EntityResponse.model_validate(entity)


@router.get("/", response_model=EntityListResponse)
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_inactive: bool = Query(False),
    current_user: CurrentUser = Depends()
):
    """List all entities accessible to the current user."""
    service = EntityService(db)
    entities, total = await service.list_entities(
        skip=skip,
        limit=limit,
        include_inactive=include_inactive
    )
    return EntityListResponse(
        entities=[EntityResponse.model_validate(e) for e in entities],
        total=total
    )


@router.get("/brief", response_model=list[EntityBriefResponse])
async def list_entities_brief(
    current_user: CurrentUser = Depends()
):
    """List all active entities (brief info for dropdowns)."""
    service = EntityService(db)
    entities, _ = await service.list_entities(
        skip=0,
        limit=1000,
        include_inactive=False
    )
    return [EntityBriefResponse.model_validate(e) for e in entities]


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    db: DbSession,
    current_user: CurrentUser = Depends()
):
    """Get a specific entity."""
    service = EntityService(db)
    entity = await service.get_entity(entity_id)

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Établissement non trouvé"
        )

    return EntityResponse.model_validate(entity)


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    data: EntityUpdate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Update an entity (admin only)."""
    service = EntityService(db)
    entity = await service.update_entity(entity_id, data)

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Établissement non trouvé"
        )

    return EntityResponse.model_validate(entity)


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: int,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Delete an entity (soft delete - admin only)."""
    service = EntityService(db)
    success = await service.delete_entity(entity_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Établissement non trouvé"
        )


# ========================
# User-Entity Assignments
# ========================


@router.post("/assignments", response_model=EntityUserAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_user_to_entity(
    data: EntityUserAssignmentCreate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Assign a user to an entity (admin only)."""
    service = EntityService(db)

    # Verify entity exists
    entity = await service.get_entity(data.entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Établissement non trouvé"
        )

    assignment = await service.assign_user_to_entity(
        user_id=data.user_id,
        entity_id=data.entity_id,
        assigned_by=current_user.id,
        is_default=data.is_default,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.assignment_reason
    )
    return EntityUserAssignmentResponse.model_validate(assignment)


@router.get("/assignments/user/{user_id}", response_model=UserWithEntitiesResponse)
async def get_user_entities(
    user_id: int,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Get all entities a user is assigned to (admin only)."""
    service = EntityService(db)
    from app.models.entity import EntityUserAssignment
    from sqlalchemy.orm import selectinload

    # Get user
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Get assignments
    assignments = await service.get_user_entities(user_id)
    default_entity = await service.get_user_default_entity(user_id)

    return UserWithEntitiesResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        can_access_all_entities=user.can_access_all_entities,
        assignments=[EntityUserAssignmentResponse.model_validate(a) for a in assignments],
        default_entity=EntityBriefResponse.model_validate(default_entity) if default_entity else None
    )


@router.put("/assignments/{assignment_id}", response_model=EntityUserAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: EntityUserAssignmentUpdate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Update a user-entity assignment (admin only)."""
    from sqlalchemy import update
    from app.models.entity import EntityUserAssignment

    result = await db.execute(
        select(EntityUserAssignment).where(EntityUserAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affectation non trouvée"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)

    await db.commit()
    await db.refresh(assignment)
    return EntityUserAssignmentResponse.model_validate(assignment)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_entity(
    assignment_id: int,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Remove a user from an entity (admin only)."""
    from sqlalchemy import select
    from app.models.entity import EntityUserAssignment

    result = await db.execute(
        select(EntityUserAssignment).where(EntityUserAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affectation non trouvée"
        )

    await EntityService(db).remove_user_from_entity(
        assignment.user_id,
        assignment.entity_id
    )


@router.get("/me/entities", response_model=list[EntityBriefResponse])
async def get_my_entities(
    db: DbSession,
    current_user: CurrentUser = Depends()
):
    """Get all entities the current user is assigned to."""
    service = EntityService(db)
    assignments = await service.get_user_entities(current_user.id)
    return [EntityBriefResponse.model_validate(a.entity) for a in assignments if a.entity]


@router.get("/me/default-entity", response_model=EntityBriefResponse | None)
async def get_my_default_entity(
    db: DbSession,
    current_user: CurrentUser = Depends()
):
    """Get the current user's default entity."""
    # Check if user has global access
    if current_user.can_access_all_entities:
        from sqlalchemy import select
        from app.models.entity import Entity
        result = await db.execute(
            select(Entity).where(Entity.is_default == True)
        )
        entity = result.scalar_one_or_none()
        if entity:
            return EntityBriefResponse.model_validate(entity)

    service = EntityService(db)
    entity = await service.get_user_default_entity(current_user.id)
    if not entity:
        # Return first accessible entity
        entities, _ = await service.list_entities(skip=0, limit=1, include_inactive=False)
        if entities:
            return EntityBriefResponse.model_validate(entities[0])
        return None

    return EntityBriefResponse.model_validate(entity)


# ========================
# Entity Services
# ========================


@router.post("/{entity_id}/services", response_model=EntityServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_entity_service(
    entity_id: int,
    data: EntityServiceCreate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Create a service within an entity (admin only)."""
    service = EntityService(db)

    # Verify entity exists
    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Établissement non trouvé"
        )

    svc = await service.create_service(entity_id, data)
    return EntityServiceResponse.model_validate(svc)


@router.get("/{entity_id}/services", response_model=EntityServiceListResponse)
async def list_entity_services(
    entity_id: int,
    include_inactive: bool = Query(False),
    current_user: CurrentUser = Depends()
):
    """List all services for an entity."""
    service = EntityService(db)
    services = await service.list_entity_services(entity_id, include_inactive)
    return EntityServiceListResponse(
        services=[EntityServiceResponse.model_validate(s) for s in services],
        total=len(services)
    )