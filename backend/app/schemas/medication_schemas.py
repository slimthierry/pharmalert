from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.medication_models import MedicationForm


class MedicationCreate(BaseModel):
    name: str
    dci: str
    atc_code: Optional[str] = None
    form: MedicationForm
    dosage_unit: str = "mg"
    manufacturer: Optional[str] = None
    contraindications: List[str] = []
    side_effects: List[str] = []


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dci: Optional[str] = None
    atc_code: Optional[str] = None
    form: Optional[MedicationForm] = None
    dosage_unit: Optional[str] = None
    manufacturer: Optional[str] = None
    contraindications: Optional[List[str]] = None
    side_effects: Optional[List[str]] = None


class MedicationResponse(BaseModel):
    id: int
    name: str
    dci: str
    atc_code: Optional[str] = None
    form: MedicationForm
    dosage_unit: str
    manufacturer: Optional[str] = None
    contraindications: List[str] = []
    side_effects: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicationListResponse(BaseModel):
    medications: List[MedicationResponse]
    total: int
