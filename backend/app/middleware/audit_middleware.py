import time
import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.models.audit_models import AuditLog

logger = logging.getLogger(__name__)

# Paths to exclude from audit logging
EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all API requests to the audit trail."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()
        user_id = self._extract_user_id(request)
        ip_address = request.client.host if request.client else None

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000)

        # Log asynchronously without blocking the response
        try:
            await self._log_request(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                entity_type="api_request",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
                ip_address=ip_address,
            )
        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")

        return response

    def _extract_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from the Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                return int(payload["sub"])
            except (ValueError, TypeError):
                return None
        return None

    async def _log_request(
        self,
        user_id: Optional[int],
        action: str,
        entity_type: str,
        details: dict,
        ip_address: Optional[str],
    ) -> None:
        """Log the request to the audit table."""
        async with AsyncSessionLocal() as session:
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                details=details,
                ip_address=ip_address,
            )
            session.add(audit_entry)
            await session.commit()
