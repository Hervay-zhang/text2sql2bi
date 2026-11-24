from app.repositories.dashboards import (
create_dashboard,
delete_dashboard,
list_dashboards,
)
from app.schemas.models import Dashboard, DashboardCreate


async def get_dashboards() -> list[Dashboard]:
    return [
        Dashboard(**item)
        for item in await list_dashboards()
    ]


async def save_dashboard(body: DashboardCreate) -> Dashboard:
    result=await create_dashboard(body)
    return Dashboard(**result)


async def remove_dashboard(dashboard_id: str) -> bool:
    return await delete_dashboard(dashboard_id)