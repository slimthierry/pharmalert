"""Application route aggregation."""

from fastapi import APIRouter

from app.controllers import (
    auth,
    medications,
    prescriptions,
    administrations,
    interactions,
    allergies,
    adverse_events,
    dashboard,
    audit,
    entities,
    settings,
)
from app.libs.fhir import (
    medication_request,
    medication_administration,
    allergy_intolerance,
)

app_router = APIRouter()

# API v1 routes
app_router.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app_router.include_router(medications.router, prefix="/api/v1/medications", tags=["Medications"])
app_router.include_router(
    prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"]
)
app_router.include_router(
    administrations.router, prefix="/api/v1/administrations", tags=["Administrations"]
)
app_router.include_router(
    interactions.router, prefix="/api/v1/interactions", tags=["Interactions"]
)
app_router.include_router(allergies.router, prefix="/api/v1/allergies", tags=["Allergies"])
app_router.include_router(
    adverse_events.router, prefix="/api/v1/adverse-events", tags=["Adverse Events"]
)
app_router.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app_router.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

# Entity & Settings routes
app_router.include_router(entities.router, prefix="/api/v1/entities", tags=["Entities"])
app_router.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])

# FHIR routes
app_router.include_router(
    medication_request.router,
    prefix="/api/fhir/MedicationRequest",
    tags=["FHIR - MedicationRequest"],
)
app_router.include_router(
    medication_administration.router,
    prefix="/api/fhir/MedicationAdministration",
    tags=["FHIR - MedicationAdministration"],
)
app_router.include_router(
    allergy_intolerance.router,
    prefix="/api/fhir/AllergyIntolerance",
    tags=["FHIR - AllergyIntolerance"],
)