"""
System configuration API endpoints.

Handles CRUD for system settings (key-value store).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_admin
from app.models.user_models import User
from app.schemas.settings_schemas import (
    ConfigGroupCreate, ConfigGroupUpdate, ConfigGroupResponse,
    SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse,
    SystemConfigListResponse, SystemConfigBulkUpdate, SettingsGroupResponse
)
from app.services.config_service import ConfigService, seed_default_configs

router = APIRouter()


# ========================
# Config Groups
# ========================


@router.get("/groups", response_model=list[ConfigGroupResponse])
async def list_config_groups(
    current_user: User = Depends(require_admin)
):
    """List all config groups (admin only)."""
    service = ConfigService(db)
    groups = await service.list_groups()
    return [ConfigGroupResponse.model_validate(g) for g in groups]


@router.post("/groups", response_model=ConfigGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_config_group(
    data: ConfigGroupCreate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Create a new config group (admin only)."""
    service = ConfigService(db)
    group = await service.create_group(
        key=data.key,
        name=data.name,
        description=data.description,
        icon=data.icon,
        display_order=data.display_order
    )
    return ConfigGroupResponse.model_validate(group)


# ========================
# SystemConfig CRUD
# ========================


@router.get("/", response_model=SystemConfigListResponse)
async def list_configs(
    group: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_admin)
):
    """List all system configs (admin only)."""
    service = ConfigService(db)
    configs, total = await service.list_configs(
        group=group,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
    return SystemConfigListResponse(
        configs=[SystemConfigResponse.model_validate(c) for c in configs],
        total=total
    )


@router.get("/grouped", response_model=list[SettingsGroupResponse])
async def get_grouped_configs(
    entity_id: Optional[int] = Query(None),
    current_user: User = Depends(require_admin)
):
    """
    Get all configs grouped by group.

    Returns a structured list of groups with their configs.
    """
    service = ConfigService(db)
    grouped = await service.get_grouped_configs(entity_id)

    result = []
    for group_data in grouped:
        group = await service.get_group(group_data["group"])
        result.append(SettingsGroupResponse(
            group=group_data["group"],
            group_name=group.name if group else group_data["group_name"],
            configs=[SystemConfigResponse.model_validate(c) for c in group_data["configs"]]
        ))

    return result


@router.get("/by-key/{key}", response_model=SystemConfigResponse)
async def get_config_by_key(
    key: str,
    entity_id: Optional[int] = Query(None),
    current_user: User = Depends(require_admin)
):
    """Get a specific config by key (admin only)."""
    service = ConfigService(db)
    config = await service.get_config_by_key(key, entity_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{key}' non trouvée"
        )

    return SystemConfigResponse.model_validate(config)


@router.post("/", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    data: SystemConfigCreate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Create a new system config (admin only)."""
    service = ConfigService(db)

    # Check if key already exists
    existing = await service.get_config_by_key(data.key, data.entity_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Configuration '{data.key}' existe déjà"
        )

    config = await service.create_config(
        key=data.key,
        group=data.group,
        value=data.value,
        description=data.description,
        display_name=data.display_name,
        is_secret=data.is_secret,
        is_required=data.is_required,
        value_type=data.value_type,
        default_value=data.default_value,
        choices=data.choices,
        is_global=data.is_global,
        entity_id=data.entity_id
    )
    return SystemConfigResponse.model_validate(config)


@router.put("/{config_id}", response_model=SystemConfigResponse)
async def update_config(
    config_id: int,
    data: SystemConfigUpdate,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Update a config entry (admin only)."""
    service = ConfigService(db)

    update_data = data.model_dump(exclude_unset=True)
    config = await service.update_config(config_id, **update_data)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration non trouvée"
        )

    return SystemConfigResponse.model_validate(config)


@router.put("/by-key/{key}", response_model=SystemConfigResponse)
async def update_config_by_key(
    key: str,
    value: str,
    entity_id: Optional[int] = Query(None),
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Update a config value by key (admin only)."""
    service = ConfigService(db)
    config = await service.update_by_key(key, value, entity_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{key}' non trouvée"
        )

    return SystemConfigResponse.model_validate(config)


@router.post("/bulk-update", response_model=list[SystemConfigResponse])
async def bulk_update_configs(
    data: SystemConfigBulkUpdate,
    entity_id: Optional[int] = Query(None),
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Update multiple configs at once (admin only)."""
    service = ConfigService(db)
    configs = await service.bulk_update(data.updates, entity_id)
    return [SystemConfigResponse.model_validate(c) for c in configs]


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """Delete a config entry (admin only)."""
    service = ConfigService(db)
    success = await service.delete_config(config_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration non trouvée"
        )


# ========================
# Public Config Access (for frontend)
# ========================


@router.get("/public/{key}")
async def get_public_config(
    key: str,
    entity_id: Optional[int] = Query(None)
):
    """
    Get a public config value (no auth required).

    Used by frontend to get brand settings, colors, etc.
    Returns value only, not full config object.
    """
    service = ConfigService(db)
    value = await service.get_value(key, entity_id=entity_id)
    return {"key": key, "value": value}


@router.get("/public/grouped")
async def get_public_grouped_configs(
    entity_id: Optional[int] = Query(None)
):
    """
    Get public configs grouped by group (no auth required).

    Returns only non-secret configs.
    """
    service = ConfigService(db)
    grouped = await service.get_grouped_configs(entity_id)

    result = []
    for group_data in grouped:
        # Filter out secret configs
        public_configs = [
            c for c in group_data["configs"]
            if not c.is_secret
        ]
        if public_configs:
            group = await service.get_group(group_data["group"])
            result.append({
                "group": group_data["group"],
                "group_name": group.name if group else group_data["group_name"],
                "icon": group_data.get("icon"),
                "configs": [
                    {"key": c.key, "value": c.value, "display_name": c.display_name}
                    for c in public_configs
                ]
            })

    return result


# ========================
# Admin: Seed Default Configs
# ========================


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_default_configurations(
    db: DbSession,
    current_user: User = Depends(require_admin)
):
    """
    Seed default configuration groups and configs.

    Creates any missing default configs. Idempotent - safe to run multiple times.
    """
    await seed_default_configs(db)
    return {"message": "Configurations par défaut créées avec succès"}