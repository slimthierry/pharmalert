from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.adverse_event_models import (
    AdverseEventSeverity,
    AdverseEventStatus,
    AdverseEventType,
)


class AdverseEventCreate(BaseModel):
    patient_ipp: str
    medication_id: Optional[int] = None
    prescription_id: Optional[int] = None
    event_type: AdverseEventType
    severity: AdverseEventSeverity
    description: str
    reported_at: Optional[datetime] = None


class AdverseEventUpdate(BaseModel):
    event_type: Optional[AdverseEventType] = None
    severity: Optional[AdverseEventSeverity] = None
    description: Optional[str] = None
    outcome: Optional[str] = None
    status: Optional[AdverseEventStatus] = None


class AdverseEventResponse(BaseModel):
    id: int
    patient_ipp: str
    medication_id: Optional[int] = None
    medication_name: Optional[str] = None
    prescription_id: Optional[int] = None
    event_type: AdverseEventType
    severity: AdverseEventSeverity
    description: str
    outcome: Optional[str] = None
    reported_by: int
    reported_by_name: Optional[str] = None
    reported_at: datetime
    status: AdverseEventStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class AdverseEventListResponse(BaseModel):
    events: List[AdverseEventResponse]
    total: int


class AdverseEventStats(BaseModel):
    total: int
    by_severity: dict
    by_type: dict
    by_status: dict
