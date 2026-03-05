from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rbac import require_admin
from app.models.user_models import User
from app.schemas.audit_schemas import AuditLogListResponse, AuditLogResponse
from app.services.audit_service import get_audit_log, list_audit_logs

router = APIRouter()


@router.get("/", response_model=AuditLogListResponse)
async def get_audit_logs(
    db: DbSession,
    current_user: User = Depends(require_admin),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List audit logs with optional filters (admin only)."""
    logs, total = await list_audit_logs(
        db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log_by_id(
    log_id: int,
    db: DbSession,
    current_user: User = Depends(require_admin),
):
    """Get a specific audit log entry (admin only)."""
    log = await get_audit_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entree d'audit non trouvee",
        )
    return AuditLogResponse.model_validate(log)
