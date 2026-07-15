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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""

    yield

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