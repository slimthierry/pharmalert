from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

from app.config.settings import settings
from app.config.database import engine, AsyncSessionLocal
from app.routes import app_router
from app.models import Base
from app.models.user_models import User, UserRole

logger = logging.getLogger(__name__)

# ─── Background sync scheduler ────────────────────────────────────────────────

_sync_task: asyncio.Task | None = None
SIH_SERVICE: "SIHSyncService | None" = None  # type: ignore

async def start_sih_scheduler() -> None:
    print("[SCHEDULER] Creating task...")
    """
    Démarre le sync SIH en arrière-plan.
    - Sync immédiate au démarrage
    - Puis toutes les 5 minutes
    """
    global SIH_SERVICE

    print("[SCHEDULER] SIH Scheduler starting...")

    try:
        from app.sih.sih_sync_service import SIHSyncService, SIHClient

        client = SIHClient(
            url=settings.SIH_URL,
            db=settings.SIH_DB,
            username=settings.SIH_USERNAME,
            password=settings.SIH_PASSWORD,
            entity_id=1,
        )
        SIH_SERVICE = SIHSyncService(client=client, entity_id=1)
        print(f"[SCHEDULER] Started — target: {settings.SIH_URL}")

        # ── Authentifier le client SIH avant sync ──
        auth_result = await asyncio.to_thread(client.authenticate)
        if not auth_result.success:
            print(f"[SCHEDULER] ❌ Auth failed: {auth_result.error}")
        else:
            print("[SCHEDULER] ✅ SIH authenticated")

        # ── Sync immédiate au démarrage ──
        try:
            stats = await SIH_SERVICE.sync_all()
            print(f"[SCHEDULER] ✅ Initial sync done: {stats.get('patients_synced', 0)} patients, {stats.get('drugs_synced', 0)} drugs")
        except Exception as e:
            print(f"[SCHEDULER] ❌ Initial sync failed: {e}")

        # ── Boucle : sync toutes les 5 minutes ──
        while True:
            await asyncio.sleep(300)  # 5 minutes
            try:
                await asyncio.to_thread(client.authenticate)
                stats = await SIH_SERVICE.sync_all()
                print(f"[SCHEDULER] 🔄 Periodic sync: {stats.get('patients_synced', 0)} patients, {stats.get('drugs_synced', 0)} drugs")
            except Exception as e:
                print(f"[SCHEDULER] ❌ Periodic sync failed: {e}")

    except Exception as e:
        print(f"[SCHEDULER] ❌ Failed to start: {e}")

    except Exception as e:
        logger.error(f"SIH Scheduler failed to start: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup et shutdown."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Setup admin user
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

    # ── Démarrer le scheduler SIH en arrière-plan ──
    print(f"[LIFESPAN] Starting scheduler... SIH_URL={settings.SIH_URL}")
    global _sync_task
    _sync_task = asyncio.create_task(start_sih_scheduler())
    print(f"[LIFESPAN] Scheduler task created: {_sync_task}")

    yield  # ← l'app tourne ici

    # ── Cleanup ──
    if _sync_task:
        _sync_task.cancel()
        try:
            await _sync_task
        except asyncio.CancelledError:
            pass
    await engine.dispose()


app = FastAPI(
    title="PharmAlert API",
    description=(
        "Module SIH de gestion des interactions médicamenteuses, "
        "validation d'ordonnances et suivi d'administration"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(app_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "pharmalert"}


@app.get("/sih/scheduler/status", tags=["SIH"])
async def sih_scheduler_status():
    """Retourne le statut du scheduler SIH et la dernière sync."""
    if SIH_SERVICE:
        return {
            "running": True,
            "last_sync": str(SIH_SERVICE.sync_stats.get("last_sync", "never")),
            "stats": SIH_SERVICE.sync_stats,
        }
    return {"running": False}
