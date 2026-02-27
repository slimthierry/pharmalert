from typing import List, Optional

from pydantic import BaseModel

from app.schemas.adverse_event_schemas import AdverseEventResponse
from app.schemas.interaction_schemas import InteractionCheckResult


class DashboardStats(BaseModel):
    pending_validations: int
    critical_interactions: int
    missed_doses_today: int
    compliance_rate: float
    total_active_prescriptions: int
    total_patients: int


class DashboardAlerts(BaseModel):
    critical_interactions: List[InteractionCheckResult]
    recent_adverse_events: List[AdverseEventResponse]


class DashboardResponse(BaseModel):
    stats: DashboardStats
    alerts: DashboardAlerts
