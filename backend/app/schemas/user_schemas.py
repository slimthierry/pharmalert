from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user_models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole
    service: Optional[str] = None
    rpps_number: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    service: Optional[str] = None
    rpps_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    service: Optional[str] = None
    rpps_number: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
