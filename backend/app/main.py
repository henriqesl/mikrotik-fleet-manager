from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.database import (
    check_database_connection,
    close_database_connection,
)

from app.core.credential_cipher import get_credential_cipher
from app.routes.routers import router as routers_router
from app.workers.polling import polling_worker
from app.routes.monitoring import router as monitoring_router

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""

    get_credential_cipher()
    polling_worker.start()

    try:
        yield

    finally:
        await polling_worker.stop()
        await close_database_connection()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for monitoring and managing MikroTik router fleets."
    ),
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    routers_router,
    prefix=settings.api_prefix,
)

app.include_router(
    monitoring_router,
    prefix=settings.api_prefix,
)

@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    """Return basic information about the API."""

    return {
        "message": f"{settings.app_name} is running."
    }


@app.get("/health", tags=["Health"])
async def health_check(response: Response) -> dict[str, str]:
    """Return the current API and database health status."""

    try:
        await check_database_connection()

    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {
            "status": "degraded",
            "environment": settings.environment,
            "database": "unavailable",
        }

    return {
        "status": "ok",
        "environment": settings.environment,
        "database": "available",
    }