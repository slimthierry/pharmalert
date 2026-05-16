from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_admin
from app.models.user_models import User
from app.schemas.auth_schemas import LoginRequest, PasswordChangeRequest, TokenResponse
from app.schemas.user_schemas import UserCreate, UserListResponse, UserResponse
from app.services.auth_service import (
    authenticate_user,
    authenticate_user_via_sih,
    create_user,
    get_user_by_email,
    list_users,
)
from app.auth.security import get_password_hash, verify_password

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: DbSession):
    """
    Authenticate and receive an access token.
    Tries Odoo SIH authentication first, then falls back to local PharmAlert auth.
    """
    # Try SIH (Odoo) authentication first
    token_response = await authenticate_user_via_sih(db, login_data)
    if token_response:
        return token_response

    # Fall back to local PharmAlert auth (admin account, etc.)
    token_response = await authenticate_user(db, login_data)
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    return token_response


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DbSession,
    current_user: User = Depends(require_admin),
):
    """Register a new user (admin only)."""
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe deja",
        )
    user = await create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """Get the current authenticated user's information."""
    return UserResponse.model_validate(current_user)


@router.put("/me/password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Change the current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect",
        )
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.flush()
    return {"message": "Mot de passe modifie avec succes"}


@router.get("/users", response_model=UserListResponse)
async def get_users(
    db: DbSession,
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
):
    """List all users (admin only)."""
    users, total = await list_users(db, skip=skip, limit=limit)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
    )
