"""
FHIR R4 compatible schemas for interoperability with Hospital Information Systems.
Simplified representations of FHIR resources.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# --- FHIR Common Types ---

class FHIRCoding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None


class FHIRCodeableConcept(BaseModel):
    coding: List[FHIRCoding] = []
    text: Optional[str] = None


class FHIRReference(BaseModel):
    reference: Optional[str] = None
    display: Optional[str] = None


class FHIRPeriod(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class FHIRQuantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = "http://unitsofmeasure.org"
    code: Optional[str] = None


# --- FHIR MedicationRequest ---

class FHIRDosageInstruction(BaseModel):
    text: Optional[str] = None
    route: Optional[FHIRCodeableConcept] = None
    doseAndRate: Optional[List[dict]] = None
    timing: Optional[dict] = None


class FHIRMedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: Optional[str] = None
    status: str  # active | on-hold | cancelled | completed | stopped
    intent: str = "order"
    medicationCodeableConcept: Optional[FHIRCodeableConcept] = None
    subject: Optional[FHIRReference] = None  # Patient
    requester: Optional[FHIRReference] = None  # Practitioner
    dosageInstruction: List[FHIRDosageInstruction] = []
    dispenseRequest: Optional[dict] = None
    authoredOn: Optional[datetime] = None


# --- FHIR MedicationAdministration ---

class FHIRMedicationAdministration(BaseModel):
    resourceType: str = "MedicationAdministration"
    id: Optional[str] = None
    status: str  # in-progress | completed | not-done
    medicationCodeableConcept: Optional[FHIRCodeableConcept] = None
    subject: Optional[FHIRReference] = None  # Patient
    performer: Optional[List[dict]] = None
    effectiveDateTime: Optional[datetime] = None
    dosage: Optional[dict] = None
    request: Optional[FHIRReference] = None  # MedicationRequest


# --- FHIR AllergyIntolerance ---

class FHIRReaction(BaseModel):
    substance: Optional[FHIRCodeableConcept] = None
    manifestation: List[FHIRCodeableConcept] = []
    severity: Optional[str] = None  # mild | moderate | severe


class FHIRAllergyIntolerance(BaseModel):
    resourceType: str = "AllergyIntolerance"
    id: Optional[str] = None
    clinicalStatus: Optional[FHIRCodeableConcept] = None
    verificationStatus: Optional[FHIRCodeableConcept] = None
    type: Optional[str] = None  # allergy | intolerance
    category: List[str] = []  # food | medication | environment | biologic
    criticality: Optional[str] = None  # low | high | unable-to-assess
    code: Optional[FHIRCodeableConcept] = None
    patient: Optional[FHIRReference] = None
    recorder: Optional[FHIRReference] = None
    reaction: List[FHIRReaction] = []
    recordedDate: Optional[datetime] = None


# --- FHIR Bundle ---

class FHIRBundleEntry(BaseModel):
    resource: dict
    fullUrl: Optional[str] = None


class FHIRBundle(BaseModel):
    resourceType: str = "Bundle"
    type: str = "searchset"
    total: int = 0
    entry: List[FHIRBundleEntry] = []
