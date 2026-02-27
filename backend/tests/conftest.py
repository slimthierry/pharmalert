import asyncio
from datetime import date, datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.base import Base
from app.models.user_models import User, UserRole
from app.models.medication_models import Medication, MedicationForm
from app.models.interaction_models import Interaction, InteractionSeverity

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email="admin@pharmalert.fr",
        name="Admin Test",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        service="Administration",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def doctor_user(db_session: AsyncSession) -> User:
    user = User(
        email="medecin@pharmalert.fr",
        name="Dr. Dupont",
        hashed_password=get_password_hash("medecin123"),
        role=UserRole.MEDECIN,
        service="Cardiologie",
        rpps_number="12345678901",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def pharmacist_user(db_session: AsyncSession) -> User:
    user = User(
        email="pharmacien@pharmalert.fr",
        name="Pharm. Martin",
        hashed_password=get_password_hash("pharmacien123"),
        role=UserRole.PHARMACIEN,
        service="Pharmacie",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def nurse_user(db_session: AsyncSession) -> User:
    user = User(
        email="infirmier@pharmalert.fr",
        name="Inf. Leroy",
        hashed_password=get_password_hash("infirmier123"),
        role=UserRole.INFIRMIER,
        service="Cardiologie",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_medications(db_session: AsyncSession) -> list[Medication]:
    meds = [
        Medication(
            name="Warfarine",
            dci="warfarine sodique",
            atc_code="B01AA03",
            form=MedicationForm.TABLET,
            dosage_unit="mg",
            manufacturer="Sanofi",
            contraindications=["grossesse", "ulcere gastrique actif"],
            side_effects=["hemorragie", "nausee"],
        ),
        Medication(
            name="Aspirine",
            dci="acide acetylsalicylique",
            atc_code="N02BA01",
            form=MedicationForm.TABLET,
            dosage_unit="mg",
            manufacturer="Bayer",
            contraindications=["ulcere gastrique", "hemophilie"],
            side_effects=["douleur gastrique", "saignement"],
        ),
        Medication(
            name="Omeprazole",
            dci="omeprazole",
            atc_code="A02BC01",
            form=MedicationForm.CAPSULE,
            dosage_unit="mg",
            manufacturer="AstraZeneca",
            contraindications=[],
            side_effects=["cephalee", "diarrhee"],
        ),
    ]
    for med in meds:
        db_session.add(med)
    await db_session.commit()
    for med in meds:
        await db_session.refresh(med)
    return meds


@pytest_asyncio.fixture
async def sample_interaction(
    db_session: AsyncSession, sample_medications: list[Medication]
) -> Interaction:
    interaction = Interaction(
        medication_a_id=sample_medications[0].id,  # Warfarine
        medication_b_id=sample_medications[1].id,  # Aspirine
        severity=InteractionSeverity.MAJOR,
        mechanism="Inhibition de l'agregation plaquettaire",
        clinical_effect="Risque hemorragique majeur",
        recommendation="Eviter l'association. Si necessaire, surveillance rapprochee de l'INR.",
        source="Thesaurus ANSM",
    )
    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)
    return interaction


def get_auth_headers(user: User) -> dict:
    """Generate authorization headers for a user."""
    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}
