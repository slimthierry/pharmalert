from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.prescription_models import (
    AdministrationRoute,
    PrescriptionStatus,
    ValidationStatus,
)
from app.schemas.interaction_schemas import InteractionCheckResult


class PrescriptionCreate(BaseModel):
    patient_ipp: str
    patient_name: str
    medication_id: int
    dosage_value: float
    dosage_unit: str = "mg"
    frequency: str
    route: AdministrationRoute = AdministrationRoute.ORAL
    start_date: date
    end_date: Optional[date] = None
    override_justification: Optional[str] = None


class PrescriptionValidate(BaseModel):
    validation_status: ValidationStatus
    validation_notes: Optional[str] = None


class PrescriptionUpdate(BaseModel):
    dosage_value: Optional[float] = None
    dosage_unit: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[AdministrationRoute] = None
    end_date: Optional[date] = None
    status: Optional[PrescriptionStatus] = None


class PrescriptionResponse(BaseModel):
    id: int
    patient_ipp: str
    patient_name: str
    prescriber_id: int
    prescriber_name: Optional[str] = None
    medication_id: int
    medication_name: Optional[str] = None
    dosage_value: float
    dosage_unit: str
    frequency: str
    route: AdministrationRoute
    start_date: date
    end_date: Optional[date] = None
    status: PrescriptionStatus
    validation_status: ValidationStatus
    validated_by: Optional[int] = None
    validator_name: Optional[str] = None
    validation_notes: Optional[str] = None
    interactions_checked: bool
    override_justification: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PrescriptionCreateResponse(BaseModel):
    prescription: PrescriptionResponse
    interactions: List[InteractionCheckResult] = []
    allergy_warnings: List[str] = []


class PrescriptionListResponse(BaseModel):
    prescriptions: List[PrescriptionResponse]
    total: int
