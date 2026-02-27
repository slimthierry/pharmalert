from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.administration_models import AdministrationStatus


class AdministrationCreate(BaseModel):
    prescription_id: int
    scheduled_at: datetime
    patient_ipp: str


class AdministrationRecord(BaseModel):
    status: AdministrationStatus
    dose_given: Optional[float] = None
    notes: Optional[str] = None
    vital_signs: Optional[Dict] = None


class AdministrationResponse(BaseModel):
    id: int
    prescription_id: int
    nurse_id: Optional[int] = None
    nurse_name: Optional[str] = None
    scheduled_at: datetime
    administered_at: Optional[datetime] = None
    dose_given: Optional[float] = None
    status: AdministrationStatus
    patient_ipp: str
    patient_name: Optional[str] = None
    medication_name: Optional[str] = None
    notes: Optional[str] = None
    vital_signs: Optional[Dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdministrationListResponse(BaseModel):
    administrations: List[AdministrationResponse]
    total: int
