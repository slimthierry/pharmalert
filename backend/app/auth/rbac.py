from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user_models import User, UserRole


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory that checks if the current user has one of the allowed roles.

    Usage:
        @router.post("/", dependencies=[Depends(require_roles([UserRole.MEDECIN]))])
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            role_names = ", ".join([r.value for r in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acces refuse. Roles autorises: {role_names}",
            )
        return current_user

    return role_checker


def check_role(user: User, allowed_roles: List[UserRole]) -> bool:
    """Check if a user has one of the allowed roles."""
    return user.role in allowed_roles


# Pre-defined role checkers
require_admin = require_roles([UserRole.ADMIN])
require_medecin = require_roles([UserRole.MEDECIN, UserRole.ADMIN])
require_pharmacien = require_roles([UserRole.PHARMACIEN, UserRole.ADMIN])
require_infirmier = require_roles([UserRole.INFIRMIER, UserRole.ADMIN])
require_preparateur = require_roles([UserRole.PREPARATEUR, UserRole.ADMIN])
require_clinical = require_roles([
    UserRole.MEDECIN,
    UserRole.PHARMACIEN,
    UserRole.INFIRMIER,
    UserRole.ADMIN,
])
