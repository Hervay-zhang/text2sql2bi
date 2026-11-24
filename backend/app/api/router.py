from fastapi import APIRouter

from app.api.routes import health, schema_catalog, queries, history, dashboards

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(schema_catalog.router)
api_router.include_router(queries.router)
api_router.include_router(history.router)
api_router.include_router(dashboards.router)
