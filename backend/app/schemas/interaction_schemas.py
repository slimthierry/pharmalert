from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.interaction_models import InteractionSeverity


class InteractionCreate(BaseModel):
    medication_a_id: int
    medication_b_id: int
    severity: InteractionSeverity
    mechanism: Optional[str] = None
    clinical_effect: str
    recommendation: str
    source: Optional[str] = None


class InteractionUpdate(BaseModel):
    severity: Optional[InteractionSeverity] = None
    mechanism: Optional[str] = None
    clinical_effect: Optional[str] = None
    recommendation: Optional[str] = None
    source: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    medication_a_id: int
    medication_a_name: Optional[str] = None
    medication_b_id: int
    medication_b_name: Optional[str] = None
    severity: InteractionSeverity
    mechanism: Optional[str] = None
    clinical_effect: str
    recommendation: str
    source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InteractionListResponse(BaseModel):
    items: List[InteractionResponse]
    total: int


class InteractionCheckRequest(BaseModel):
    medication_ids: List[int]
    patient_ipp: Optional[str] = None


class InteractionCheckResult(BaseModel):
    medication_a_id: int
    medication_a_name: str
    medication_b_id: int
    medication_b_name: str
    severity: InteractionSeverity
    clinical_effect: str
    recommendation: str


class InteractionCheckResponse(BaseModel):
    interactions: List[InteractionCheckResult]
    has_contraindicated: bool
    has_major: bool
    allergy_warnings: List[str] = []


class InteractionMatrixRequest(BaseModel):
    """Request body for getting interaction matrix between medications."""
    medication_ids: List[int]


class InteractionMatrixEntry(BaseModel):
    medication_a_id: int
    medication_b_id: int
    severity: Optional[InteractionSeverity] = None


class InteractionMatrixResponse(BaseModel):
    medications: List[dict]
    matrix: List[InteractionMatrixEntry]
