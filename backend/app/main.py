from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

from app.config.settings import settings
from app.config.database import engine, AsyncSessionLocal
from app.routes import app_router
from app.models import Base
from app.models.user_models import User, UserRole


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == 'admin@pharmalert.com'))
        existing = result.scalar_one_or_none()
        if existing:
            existing.hashed_password = bcrypt.hashpw(
                'admin123'.encode(), bcrypt.gensalt()
            ).decode()
            await session.commit()
            print('Admin updated: admin@pharmalert.com / admin123')
        else:
            hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            admin = User(
                email='admin@pharmalert.com',
                name='Admin',
                hashed_password=hashed,
                role=UserRole.ADMIN,
            )
            session.add(admin)
            await session.commit()
            print('Admin created: admin@pharmalert.com / admin123')

        meds_result = await session.execute(select(User))
        if meds_result.scalars().first() is not None:
            print('Data already seeded, skipping.')
        else:
            print('Data seeded.')

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

# Register all routes from app_router
app.include_router(app_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pharmalert"}
