from datetime import datetime
from typing import Optional

import bcrypt
import xmlrpc.client
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.config.settings import settings
from app.models.user_models import User, UserRole
from app.schemas.auth_schemas import LoginRequest, TokenResponse
from app.schemas.user_schemas import UserCreate


# ─── Odoo / SIH authentication ──────────────────────────────────────────────

def _sih_authenticate(login: str, password: str) -> Optional[dict]:
    """
    Authentifie via Odoo XML-RPC et retourne les infos utilisateur.
    Retourne None si l'authentification échoue.
    """
    try:
        url = settings.SIH_URL.rstrip("/")
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(settings.SIH_DB, login, password, {})
        if not uid:
            return None

        # Lire les infos utilisateur et groupes Odoo
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        user_data = models.execute_kw(
            settings.SIH_DB, uid, password,
            'res.users', 'read', [uid],
            {'fields': ['name', 'login', 'groups_id']}
        )[0]

        groups = user_data.get('groups_id', [])
        return {
            "uid": uid,
            "name": user_data.get('name', login),
            "login": user_data.get('login', login),
            "groups": groups,
        }
    except Exception:
        return None


def _map_sih_groups_to_role(groups: list) -> UserRole:
    """
    Map les groupes Odoo Likmed vers les rôles PharmAlert.
    """
    # Group IDs typiques dans Odoo Likmed (à adapter selon la config Odoo)
    # Ces IDs sont结构els et peuvent varier — on fait une heuristique
    group_map = {
        'medecin':    [3, 4, 5],   # médecin / médecin chef
        'pharmacien': [6, 7],       # pharmacien / pharmacist
        'infirmier':  [8, 9, 10],   # infirmier
        'preparateur': [11],        # préparateur
        'admin':      [1, 2],       # admin / manager
    }

    for role, gids in group_map.items():
        for gid in gids:
            if gid in groups:
                return UserRole(role)

    return UserRole.INFIRMIER  # défaut


async def authenticate_user_via_sih(
    db: AsyncSession, login_data: LoginRequest
) -> Optional[TokenResponse]:
    """
    Authentifie via Odoo SIH et retourne un TokenResponse.
    Crée ou met à jour l'utilisateur PharmAlert correspondant.
    """
    sih_user = _sih_authenticate(login_data.email, login_data.password)
    if not sih_user:
        return None

    # Chercher l'utilisateur existant
    result = await db.execute(select(User).where(User.email == sih_user['login']))
    user = result.scalar_one_or_none()

    role = _map_sih_groups_to_role(sih_user['groups'])

    if user is None:
        # Créer un nouvel utilisateur depuis SIH
        user = User(
            email=sih_user['login'],
            name=sih_user['name'],
            hashed_password=get_password_hash(settings.SECRET_KEY),  # mot de passe non utilisé
            role=role,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # Mettre à jour le nom et le rôle depuis SIH
        user.name = sih_user['name']
        user.role = role
        await db.flush()

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        role=user.role.value,
        name=user.name,
    )


# ─── Local authentication ─────────────────────────────────────────────────────

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
