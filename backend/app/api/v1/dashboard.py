from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.dashboard_schemas import DashboardResponse
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(db: DbSession, current_user: CurrentUser):
    """Get dashboard statistics and alerts."""
    return await get_dashboard_data(db)
