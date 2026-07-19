import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.credential_cipher import get_credential_cipher
from app.core.logging import configure_logging
from app.db.database import (
    check_database_connection,
    close_database_connection,
)
from app.routes.monitoring import router as monitoring_router
from app.routes.routers import router as routers_router
from app.workers.polling import polling_worker


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""

    configure_logging()
    get_credential_cipher()

    if settings.polling_enabled:
        polling_worker.start()

    try:
        yield

    finally:
        if settings.polling_enabled:
            await polling_worker.stop()

        await close_database_connection()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for monitoring and managing "
        "MikroTik router fleets."
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


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(
    request: Request,
    exception: SQLAlchemyError,
) -> JSONResponse:
    """Return a safe response for unexpected database failures."""

    logger.exception(
        "Database error while processing %s %s.",
        request.method,
        request.url.path,
        exc_info=exception,
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "The database is temporarily unavailable."
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return a safe response for unhandled application errors."""

    logger.exception(
        "Unexpected error while processing %s %s.",
        request.method,
        request.url.path,
        exc_info=exception,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred."
        },
    )


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    """Return basic information about the API."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": f"{settings.app_name} is running.",
    }


@app.get("/health", tags=["Health"])
async def health_check(
    response: Response,
) -> dict[str, str | bool]:
    """Return the current API and database health status."""

    try:
        await check_database_connection()

    except SQLAlchemyError:
        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return {
            "status": "degraded",
            "environment": settings.environment,
            "database": "unavailable",
            "polling_enabled": settings.polling_enabled,
        }

    return {
        "status": "ok",
        "environment": settings.environment,
        "database": "available",
        "polling_enabled": settings.polling_enabled,
    }