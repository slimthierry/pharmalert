"""
Pydantic schemas for Entity models.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ========================
# Entity (Établissement)
# ========================


class EntityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    max_users: int = Field(default=50, ge=1)


class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    max_users: Optional[int] = Field(None, ge=1)


class EntityResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    is_default: bool
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    max_users: int
    is_subscription_valid: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    entities: list[EntityResponse]
    total: int


class EntityBriefResponse(BaseModel):
    """Minimal entity info for dropdowns/selectors."""
    id: int
    name: str
    code: str
    logo_url: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# ========================
# EntityUserAssignment
# ========================


class EntityUserAssignmentCreate(BaseModel):
    user_id: int
    entity_id: int
    is_default: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assignment_reason: Optional[str] = None


class EntityUserAssignmentUpdate(BaseModel):
    is_default: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    assignment_reason: Optional[str] = None


class EntityUserAssignmentResponse(BaseModel):
    id: int
    user_id: int
    entity_id: int
    is_default: bool
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool
    assigned_by: Optional[int] = None
    assignment_reason: Optional[str] = None
    is_valid: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserWithEntitiesResponse(BaseModel):
    """User info with their entity assignments."""
    id: int
    email: str
    name: str
    role: str
    can_access_all_entities: bool
    assignments: list[EntityUserAssignmentResponse]
    default_entity: Optional[EntityBriefResponse] = None

    model_config = {"from_attributes": True}


# ========================
# EntityService
# ========================


class EntityServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = None
    display_order: int = 0


class EntityServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class EntityServiceResponse(BaseModel):
    id: int
    entity_id: int
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool
    display_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EntityServiceListResponse(BaseModel):
    services: list[EntityServiceResponse]
    total: int