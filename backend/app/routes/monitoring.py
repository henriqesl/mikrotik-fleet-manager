from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.core.config import settings
from app.schemas.monitoring import (
    MonitoringStatusResponse,
    PollingSummaryResponse,
)
from app.workers.polling import (
    PollingCycleInProgressError,
    polling_worker,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


@router.get(
    "/status",
    response_model=MonitoringStatusResponse,
)
async def get_monitoring_status() -> MonitoringStatusResponse:
    """Return the current polling worker status."""

    worker_state = polling_worker.state

    last_summary = None

    if worker_state.last_summary is not None:
        last_summary = PollingSummaryResponse(
            total=worker_state.last_summary.total,
            online=worker_state.last_summary.online,
            offline=worker_state.last_summary.offline,
            errors=worker_state.last_summary.errors,
        )

    return MonitoringStatusResponse(
        worker_running=worker_state.is_running,
        cycle_in_progress=worker_state.cycle_in_progress,
        poll_interval_seconds=settings.poll_interval_seconds,
        last_started_at=worker_state.last_started_at,
        last_finished_at=worker_state.last_finished_at,
        last_summary=last_summary,
        last_error=worker_state.last_error,
    )


@router.post(
    "/poll",
    response_model=PollingSummaryResponse,
)
async def trigger_polling_cycle() -> PollingSummaryResponse:
    """Manually execute one router polling cycle."""

    try:
        summary = await polling_worker.run_once()

    except PollingCycleInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A router polling cycle is already running.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The router polling cycle failed.",
        ) from exc

    return PollingSummaryResponse(
        total=summary.total,
        online=summary.online,
        offline=summary.offline,
        errors=summary.errors,
    )