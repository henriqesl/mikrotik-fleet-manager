from datetime import datetime

from pydantic import BaseModel


class PollingSummaryResponse(BaseModel):
    """Summary returned after a router polling cycle."""

    total: int
    online: int
    offline: int
    errors: int


class MonitoringStatusResponse(BaseModel):
    """Current runtime status of the polling worker."""

    worker_running: bool
    cycle_in_progress: bool
    poll_interval_seconds: int

    last_started_at: datetime | None
    last_finished_at: datetime | None

    last_summary: PollingSummaryResponse | None
    last_error: str | None