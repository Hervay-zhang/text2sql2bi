from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.clients import close_clients
from app.core.config import settings
from app.core.database import close_pools


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_clients()
    await close_pools()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Text2SQL2BI",
        version="0.2.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(
        api_router,
        prefix=settings.API_PREFIX,
    )

    @application.get("/")
    async def root() -> dict:
        return {
            "name": "Text2SQL2BI",
            "docs": "/docs",
            "health": f"{settings.API_PREFIX}/health",
        }

    return application


app = create_app()