
from app.repositories.query_history import delete_query_history, list_query_history
from app.schemas.models import QueryHistoryRecord


async def get_query_history(
        limit:int,
) ->list[QueryHistoryRecord]:
    
    return[
            QueryHistoryRecord(**item)
            for item in await list_query_history(limit)
    ]

async def remove_query_history(history_id:int) ->bool:
    return await delete_query_history(history_id)