from datetime import datetime

from pydantic import BaseModel


class PollingSummaryResponse(BaseModel):
    """Summary returned after a router polling batch."""

    total: int
    online: int
    offline: int
    errors: int


class PollingRequestResponse(BaseModel):
    """Result returned after queuing polling work."""

    queued: int
    requested_at: datetime


class MonitoringStatusResponse(BaseModel):
    """Database-backed monitoring scheduler status."""

    polling_enabled: bool
    polling_mode: str
    cycle_in_progress: bool
    active_routers: int
    due_routers: int
    leased_routers: int
    poll_interval_seconds: int
    last_started_at: datetime | None
    last_finished_at: datetime | None