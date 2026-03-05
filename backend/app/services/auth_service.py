from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.models.user_models import User, UserRole
from app.schemas.auth_schemas import LoginRequest, TokenResponse
from app.schemas.user_schemas import UserCreate


async def authenticate_user(
    db: AsyncSession, login_data: LoginRequest
) -> Optional[TokenResponse]:
    """Authenticate a user and return a token response."""
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        return None

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        role=user.role.value,
        name=user.name,
    )


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        service=user_data.service,
        rpps_number=user_data.rpps_number,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession,
    role: Optional[UserRole] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[User], int]:
    """List users with optional role filter."""
    query = select(User)
    if role:
        query = query.where(User.role == role)

    # Count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Fetch
    result = await db.execute(query.offset(skip).limit(limit).order_by(User.id))
    users = list(result.scalars().all())

    return users, total
