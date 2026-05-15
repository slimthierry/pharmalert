from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# ─── Auth ────────────────────────────────────────────────────────────────────

class SIHLoginRequest(BaseModel):
    login: str
    password: str


class SIHLoginResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None


class SIHTokenData(BaseModel):
    token: str
    uid: int
    user: str
    session_id: str
    permissions: List[str]


# ─── Patients ────────────────────────────────────────────────────────────────

class SIHPatient(BaseModel):
    id: int
    reference: Optional[str] = None
    name: str
    last_name: str
    first_name: str
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_hospitalized: bool = False
    has_insurance: bool = False
    patient_insurance_id: Optional[str] = None


# ─── Drugs / Medications ───────────────────────────────────────────────────────

class SIHDrug(BaseModel):
    id: int
    name: str
    code: Optional[str] = None  # CIP code
    dosage: Optional[str] = None
    amn_number: Optional[str] = None  # AMM number
    manufacturer: Optional[str] = None
    drug_type: Optional[str] = None
    form: Optional[str] = None
    dci: Optional[str] = None  # Dénomination Commune Internationale
    current_stock: float = 0.0
    stock_status: str = "in_stock"  # out_of_stock, low_stock, in_stock
    active: bool = True


# ─── Prescriptions / Orders ──────────────────────────────────────────────────

class SIHOrderLine(BaseModel):
    id: int
    drug_id: int
    drug_name: str
    quantity: str
    dosage: Optional[str] = None
    dose_per_take: Optional[str] = None
    frequency: Optional[str] = None
    scheduled_times: Optional[str] = None
    route: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[int] = None
    meal_relation: Optional[str] = None
    instructions: Optional[str] = None


class SIHOrder(BaseModel):
    id: int
    name: str
    date: str
    patient_id: int
    patient_name: str
    doctor_name: Optional[str] = None
    service: Optional[str] = None
    state: str  # draft, done, invoiced, cancelled
    order_lines: List[SIHOrderLine] = []
    notes: Optional[str] = None


# ─── Allergies ───────────────────────────────────────────────────────────────

class SIHAllergy(BaseModel):
    id: int
    patient_id: int
    allergy_name: str
    date: Optional[str] = None
    note: Optional[str] = None


# ─── Sync Status ─────────────────────────────────────────────────────────────

class SIHToken(BaseModel):
    token: str
    uid: int
    session_id: str


class SIHSyncStatus(BaseModel):
    connected: bool
    last_sync: Optional[datetime] = None
    patients_count: int = 0
    drugs_count: int = 0
    orders_count: int = 0
    error: Optional[str] = None