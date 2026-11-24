#提供查询历史接口
from fastapi import APIRouter, Query, HTTPException

from app.schemas.history import get_query_history, remove_query_history
from app.schemas.models import QueryHistoryRecord

router = APIRouter(prefix="/history", tags=["history"])
@router.get("", response_model=list[QueryHistoryRecord])
async def history_list(
    limit: int = Query(default=100, ge=1, le=200),
) -> list[QueryHistoryRecord]:
    return await get_query_history(limit)


@router.delete("/{history_id}", status_code=204)
async def history_delete(history_id: int) -> None:
    if not await remove_query_history(history_id):
        raise HTTPException(
            status_code=404,
            detail="查询记录不存在",
        )