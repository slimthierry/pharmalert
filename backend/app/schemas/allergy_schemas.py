from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.allergy_models import AllergenType, AllergySeverity, ReactionType


class AllergyCreate(BaseModel):
    patient_ipp: str
    allergen_type: AllergenType
    allergen_name: str
    atc_code: Optional[str] = None
    severity: AllergySeverity = AllergySeverity.MODERATE
    reaction_type: ReactionType = ReactionType.OTHER
    confirmed: bool = False


class AllergyUpdate(BaseModel):
    allergen_type: Optional[AllergenType] = None
    allergen_name: Optional[str] = None
    atc_code: Optional[str] = None
    severity: Optional[AllergySeverity] = None
    reaction_type: Optional[ReactionType] = None
    confirmed: Optional[bool] = None


class AllergyResponse(BaseModel):
    id: int
    patient_ipp: str
    allergen_type: AllergenType
    allergen_name: str
    atc_code: Optional[str] = None
    severity: AllergySeverity
    reaction_type: ReactionType
    confirmed: bool
    reported_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AllergyListResponse(BaseModel):
    items: List[AllergyResponse]
    total: int
