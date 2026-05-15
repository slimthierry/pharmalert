"""
Service layer for Entity management.

Handles business logic for multi-entity support.
"""

from datetime import date
from typing import Optional

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entity import Entity, EntityUserAssignment, EntityService as EntityServiceModel
from app.models.user_models import User
from app.schemas.entity_schemas import EntityCreate, EntityUpdate, EntityServiceCreate


class EntityService:
    """Business logic for Entity operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================
    # Entity CRUD
    # ========================

    async def create_entity(self, data: EntityCreate, created_by: int) -> Entity:
        """Create a new entity."""
        entity = Entity(**data.model_dump())
        self.db.add(entity)
        await self.db.flush()

        # If this is the first entity, make it default
        result = await self.db.execute(select(Entity).where(Entity.is_default == True))
        if result.scalars().first() is None:
            entity.is_default = True

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID."""
        result = await self.db.execute(
            select(Entity).where(Entity.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_entity_by_code(self, code: str) -> Optional[Entity]:
        """Get entity by code."""
        result = await self.db.execute(
            select(Entity).where(Entity.code == code)
        )
        return result.scalar_one_or_none()

    async def list_entities(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> tuple[list[Entity], int]:
        """List all entities with pagination."""
        query = select(Entity)

        if not include_inactive:
            query = query.where(Entity.is_active == True)

        query = query.order_by(Entity.name).offset(skip).limit(limit)

        result = await self.db.execute(query)
        entities = result.scalars().all()

        # Count total
        total_query = select(func.count(Entity.id)).select_from(Entity)
        if not include_inactive:
            total_query = total_query.where(Entity.is_active == True)
        total = await self.db.scalar(total_query)

        return list(entities), total or 0

    async def update_entity(self, entity_id: int, data: EntityUpdate) -> Optional[Entity]:
        """Update an entity."""
        entity = await self.get_entity(entity_id)
        if not entity:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        # If setting as default, unset other defaults
        if data.is_default is True:
            await self.db.execute(
                select(Entity).where(
                    and_(Entity.is_default == True, Entity.id != entity_id)
                )
            )
            await self.db.flush()

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity (soft delete by setting inactive)."""
        entity = await self.get_entity(entity_id)
        if not entity:
            return False

        entity.is_active = False
        await self.db.commit()
        return True

    # ========================
    # User-Entity Assignment
    # ========================

    async def assign_user_to_entity(
        self,
        user_id: int,
        entity_id: int,
        assigned_by: int,
        is_default: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        reason: Optional[str] = None
    ) -> EntityUserAssignment:
        """Assign a user to an entity."""
        # Check if assignment already exists
        result = await self.db.execute(
            select(EntityUserAssignment).where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.entity_id == entity_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.is_active = True
            existing.start_date = start_date
            existing.end_date = end_date
            existing.assigned_by = assigned_by
            existing.assignment_reason = reason
            if is_default:
                existing.is_default = True
                await self._unset_other_defaults(user_id, existing.id)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        # Create new
        assignment = EntityUserAssignment(
            user_id=user_id,
            entity_id=entity_id,
            assigned_by=assigned_by,
            is_default=is_default,
            start_date=start_date,
            end_date=end_date,
            assignment_reason=reason
        )
        self.db.add(assignment)
        await self.db.flush()

        if is_default:
            await self._unset_other_defaults(user_id, assignment.id)

        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def _unset_other_defaults(self, user_id: int, exclude_id: int) -> None:
        """Unset is_default on all other assignments for this user."""
        from sqlalchemy import update
        await self.db.execute(
            update(EntityUserAssignment)
            .where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.id != exclude_id
                )
            )
            .values(is_default=False)
        )

    async def remove_user_from_entity(self, user_id: int, entity_id: int) -> bool:
        """Remove a user from an entity (soft delete)."""
        result = await self.db.execute(
            select(EntityUserAssignment).where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.entity_id == entity_id
                )
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            return False

        assignment.is_active = False
        await self.db.commit()
        return True

    async def get_user_entities(self, user_id: int) -> list[EntityUserAssignment]:
        """Get all entities a user is assigned to."""
        result = await self.db.execute(
            select(EntityUserAssignment)
            .options(selectinload(EntityUserAssignment.entity))
            .where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.is_active == True
                )
            )
        )
        return list(result.scalars().all())

    async def get_user_default_entity(self, user_id: int) -> Optional[Entity]:
        """Get the default entity for a user."""
        result = await self.db.execute(
            select(EntityUserAssignment)
            .options(selectinload(EntityUserAssignment.entity))
            .where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.is_default == True,
                    EntityUserAssignment.is_active == True
                )
            )
        )
        assignment = result.scalar_one_or_none()
        return assignment.entity if assignment else None

    async def can_user_access_entity(self, user_id: int, entity_id: int) -> bool:
        """Check if a user can access a specific entity."""
        # Check if user is admin with global access
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and user.can_access_all_entities:
            return True

        # Check assignment
        result = await self.db.execute(
            select(EntityUserAssignment).where(
                and_(
                    EntityUserAssignment.user_id == user_id,
                    EntityUserAssignment.entity_id == entity_id,
                    EntityUserAssignment.is_active == True
                )
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            return False

        return True  # assignment exists and is active

    # ========================
    # Entity Services
    # ========================

    async def create_service(self, entity_id: int, data: EntityServiceCreate) -> EntityServiceModel:
        """Create a service within an entity."""
        service = EntityServiceModel(entity_id=entity_id, **data.model_dump())
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service

    async def list_entity_services(
        self,
        entity_id: int,
        include_inactive: bool = False
    ) -> list[EntityServiceModel]:
        """List all services for an entity."""
        query = select(EntityServiceModel).where(EntityServiceModel.entity_id == entity_id)
        if not include_inactive:
            query = query.where(EntityServiceModel.is_active == True)
        query = query.order_by(EntityServiceModel.display_order, EntityServiceModel.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_service(
        self,
        service_id: int,
        data: EntityServiceCreate
    ) -> Optional[EntityServiceModel]:
        """Update a service."""
        result = await self.db.execute(
            select(EntityServiceModel).where(EntityServiceModel.id == service_id)
        )
        service = result.scalar_one_or_none()
        if not service:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        await self.db.commit()
        await self.db.refresh(service)
        return service

    async def delete_service(self, service_id: int) -> bool:
        """Delete a service."""
        result = await self.db.execute(
            select(EntityServiceModel).where(EntityServiceModel.id == service_id)
        )
        service = result.scalar_one_or_none()
        if not service:
            return False

        service.is_active = False
        await self.db.commit()
        return True