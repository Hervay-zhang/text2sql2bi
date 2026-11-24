from fastapi import APIRouter

from app.schemas.models import QueryResponse, QueryRequest
from app.services.query import run_query

router = APIRouter(tags=["query"],prefix="/query")


@router.post("", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    return await run_query(body)