"""
Entity Context Middleware.

Provides request-level entity context for multi-tenant support.
Extracts the current entity from:
1. X-Entity-ID header
2. JWT token claims (if embedded)
3. User's default entity assignment

The entity context is stored in request.state and can be accessed
via `request.state.entity_id` in any route handler.
"""

import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.auth.security import decode_access_token

logger = logging.getLogger(__name__)

# Paths that don't require entity context
EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/settings/public",
}


class EntityContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts and validates entity context from requests.

    Sets `request.state.entity_id` for use in route handlers.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # Skip if path doesn't start with /api/
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        entity_id: Optional[int] = None

        # 1. Try X-Entity-ID header
        entity_header = request.headers.get("X-Entity-ID")
        if entity_header:
            try:
                entity_id = int(entity_header)
                request.state.entity_id = entity_id
                request.state.entity_source = "header"
                return await call_next(request)
            except ValueError:
                logger.warning(f"Invalid X-Entity-ID header: {entity_header}")

        # 2. Try JWT token (if present)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)

            if payload:
                # Check for embedded entity_id in token
                if "entity_id" in payload:
                    try:
                        entity_id = int(payload["entity_id"])
                        request.state.entity_id = entity_id
                        request.state.entity_source = "token"
                        return await call_next(request)
                    except (ValueError, TypeError):
                        pass

                # Check for default_entity_id in token
                if "default_entity_id" in payload:
                    try:
                        entity_id = int(payload["default_entity_id"])
                        request.state.entity_id = entity_id
                        request.state.entity_source = "token_default"
                        return await call_next(request)
                    except (ValueError, TypeError):
                        pass

        # 3. No entity context found
        # For now, allow the request to proceed without entity filtering
        # (global admins or single-entity deployments)
        request.state.entity_id = None
        request.state.entity_source = "none"

        return await call_next(request)


def get_entity_id(request: Request) -> Optional[int]:
    """
    Get the current entity ID from request state.

    Usage in route handlers:
        entity_id = get_entity_id(request)
    """
    return getattr(request.state, "entity_id", None)


def require_entity_id(request: Request) -> int:
    """
    Get the current entity ID, raising an error if not set.

    Use this for routes that require entity context.
    """
    entity_id = get_entity_id(request)
    if entity_id is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Entity context required. Set X-Entity-ID header or use a user with entity assignment."
        )
    return entity_id