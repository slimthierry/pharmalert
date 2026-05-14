"""
Pydantic schemas for SystemConfig models.
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


# ========================
# ConfigGroup
# ========================


class ConfigGroupCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0


class ConfigGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ConfigGroupResponse(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int
    is_active: bool

    model_config = {"from_attributes": True}


# ========================
# SystemConfig
# ========================


class SystemConfigCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: Optional[str] = None
    group: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_name: Optional[str] = None
    is_secret: bool = False
    is_required: bool = False
    is_editable: bool = True
    value_type: str = "string"
    default_value: Optional[str] = None
    choices: Optional[str] = None
    is_global: bool = True
    entity_id: Optional[int] = None


class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    is_secret: Optional[bool] = None
    is_required: Optional[bool] = None
    is_editable: Optional[bool] = None
    default_value: Optional[str] = None
    choices: Optional[str] = None
    is_global: Optional[bool] = None
    entity_id: Optional[int] = None


class SystemConfigResponse(BaseModel):
    id: int
    key: str
    value: Optional[str] = None
    group: str
    description: Optional[str] = None
    display_name: Optional[str] = None
    is_secret: bool
    is_required: bool
    is_editable: bool
    value_type: str
    default_value: Optional[str] = None
    choices: Optional[str] = None
    is_global: bool
    entity_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemConfigListResponse(BaseModel):
    configs: list[SystemConfigResponse]
    total: int


class SystemConfigBulkUpdate(BaseModel):
    """Update multiple config values at once."""
    updates: list[dict] = Field(
        ...,
        description="List of {key: str, value: str} objects to update"
    )


class SettingsGroupResponse(BaseModel):
    """All configs for a specific group."""
    group: str
    group_name: str
    configs: list[SystemConfigResponse]