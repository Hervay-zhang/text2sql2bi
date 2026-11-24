from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.models import Dashboard, DashboardCreate
from app.services.dashboards import (
get_dashboards,
remove_dashboard,
save_dashboard,
)

router = APIRouter(
    prefix="/dashboards",
    tags=["dashboards"],
)


@router.get("", response_model=list[Dashboard])
async def dashboards() -> list[Dashboard]:
    return await get_dashboards()


@router.post("", response_model=Dashboard)
async def dashboard_create(body: DashboardCreate) -> Dashboard:
    return await save_dashboard(body)


@router.delete("/{dashboard_id}", status_code=204)
async def dashboard_delete(dashboard_id: UUID) -> None:
    if not await remove_dashboard(str(dashboard_id)):
        raise HTTPException(
            status_code=404,
            detail="看板不存在",
        )