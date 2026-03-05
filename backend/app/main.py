from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine
from app.middleware.audit_middleware import AuditMiddleware
from app.loggers import setup_logging
from app.routes import app_router
    auth,
    medications,
    prescriptions,
    administrations,
    interactions,
    allergies,
    adverse_events,
    dashboard,
    audit,
)
from app.libs.fhir import (
    medication_request,
    medication_administration,
    allergy_intolerance,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    yield
    await engine.dispose()
app = FastAPI(
    title="PharmAlert API",
    description=(
        "Module SIH de gestion des interactions medicamenteuses, "
        "validation d'ordonnances et suivi d'administration"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware
app.add_middleware(AuditMiddleware)

# API v1 routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(medications.router, prefix="/api/v1/medications", tags=["Medications"])
app.include_router(
    prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"]
)
app.include_router(
    administrations.router, prefix="/api/v1/administrations", tags=["Administrations"]
)
app.include_router(
    interactions.router, prefix="/api/v1/interactions", tags=["Interactions"]
)
app.include_router(allergies.router, prefix="/api/v1/allergies", tags=["Allergies"])
app.include_router(
    adverse_events.router, prefix="/api/v1/adverse-events", tags=["Adverse Events"]
)
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

# FHIR routes
app.include_router(
    medication_request.router,
    prefix="/api/fhir/MedicationRequest",
    tags=["FHIR - MedicationRequest"],
)
app.include_router(
    medication_administration.router,
    prefix="/api/fhir/MedicationAdministration",
    tags=["FHIR - MedicationAdministration"],
)
app.include_router(
    allergy_intolerance.router,
    prefix="/api/fhir/AllergyIntolerance",
    tags=["FHIR - AllergyIntolerance"],
)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pharmalert"}
