from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for monitoring and managing MikroTik router fleets."
    ),
    version=settings.app_version,
    debug=settings.debug,
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
async def health_check() -> dict[str, str]:
    """Return the current health status of the API."""

    return {
        "status": "ok",
        "environment": settings.environment,
    }