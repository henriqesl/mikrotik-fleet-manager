from datetime import datetime, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_database_session
from app.repositories.router import RouterRepository
from app.schemas.monitoring import (
    MonitoringStatusResponse,
    PollingRequestResponse,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


@router.get(
    "/status",
    response_model=MonitoringStatusResponse,
)
async def get_monitoring_status(
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
) -> MonitoringStatusResponse:
    """Return database-backed polling scheduler information."""

    now = datetime.now(timezone.utc)
    repository = RouterRepository(session)

    overview = await repository.get_polling_overview(
        now=now,
    )

    return MonitoringStatusResponse(
        polling_enabled=settings.polling_enabled,
        polling_mode="standalone",
        cycle_in_progress=overview.leased_routers > 0,
        active_routers=overview.active_routers,
        due_routers=overview.due_routers,
        leased_routers=overview.leased_routers,
        poll_interval_seconds=settings.poll_interval_seconds,
        last_started_at=overview.last_started_at,
        last_finished_at=overview.last_finished_at,
    )


@router.post(
    "/poll",
    response_model=PollingRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_fleet_polling(
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
) -> PollingRequestResponse:
    """Queue all available active routers for immediate polling."""

    requested_at = datetime.now(timezone.utc)
    repository = RouterRepository(session)

    queued = await repository.queue_all_active_routers(
        now=requested_at,
    )

    await session.commit()

    return PollingRequestResponse(
        queued=queued,
        requested_at=requested_at,
    )


@router.post(
    "/routers/{router_id}/poll",
    response_model=PollingRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_router_polling(
    router_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
) -> PollingRequestResponse:
    """Queue one router for immediate polling."""

    requested_at = datetime.now(timezone.utc)
    repository = RouterRepository(session)

    result = await repository.queue_router_for_polling(
        router_id=router_id,
        now=requested_at,
    )

    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found.",
        )

    if result == "inactive":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The router is disabled.",
        )

    if result == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The router is already being polled.",
        )

    await session.commit()

    return PollingRequestResponse(
        queued=1,
        requested_at=requested_at,
    )