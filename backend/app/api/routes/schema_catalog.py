#Schema路由
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.models import SchemaSyncResponse
from app.services.schema_catalog import sync_schema

router = APIRouter(
    prefix="/schema",
    tags=["schema"],
)

@router.post(
    "/sync",
    response_model=SchemaSyncResponse,
)

async def schema_sync() -> SchemaSyncResponse:
    try:
        nums=await sync_schema()
        return SchemaSyncResponse(
            tables=nums,
            collection=settings.QDRANT_COLLECTION,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Schema同步失败：{exc}",
        )