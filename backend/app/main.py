from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.entity_context import EntityContextMiddleware
from app.loggers import setup_logging
from app.routes import app_router
from app.libs.event_loop import init_event_loop, _policy_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    init_event_loop()
    yield
    if _policy_instance:
        _policy_instance.close()
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

# Entity context middleware (multi-tenant)
app.add_middleware(EntityContextMiddleware)

# Register all routes from app_router
app.include_router(app_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pharmalert"}
