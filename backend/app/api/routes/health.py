from fastapi import APIRouter

from app.core.database import ping_database

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    database = await ping_database()
    return {
        "status": "ok" if database else "degraded",
        "database": database,
    }