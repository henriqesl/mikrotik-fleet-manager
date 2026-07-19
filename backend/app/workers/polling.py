import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.services.polling import (
    PollingCycleSummary,
    poll_all_routers_once,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PollingWorkerState:
    """Runtime information about the automatic polling worker."""

    is_running: bool = False
    last_started_at: datetime | None = None
    last_finished_at: datetime | None = None
    last_summary: PollingCycleSummary | None = None
    last_error: str | None = None


class PollingWorker:
    """Run router polling cycles at a configured interval."""

    def __init__(self) -> None:
        self.state = PollingWorkerState()

        self._task: asyncio.Task[None] | None = None
        self._stop_event: asyncio.Event | None = None

    def start(self) -> None:
        """Start the polling worker if it is not already running."""

        if self._task is not None and not self._task.done():
            return

        self._stop_event = asyncio.Event()

        self._task = asyncio.create_task(
            self._run(),
            name="argos-router-polling-worker",
        )

    async def stop(self) -> None:
        """Request a graceful worker shutdown."""

        if self._task is None:
            return

        if self._stop_event is not None:
            self._stop_event.set()

        try:
            await self._task
        finally:
            self._task = None
            self._stop_event = None

    async def _run(self) -> None:
        """Run polling cycles until shutdown is requested."""

        if self._stop_event is None:
            return

        self.state.is_running = True

        logger.info(
            "ARGOS polling worker started with interval of %s seconds.",
            settings.poll_interval_seconds,
        )

        try:
            while not self._stop_event.is_set():
                await self._run_cycle()

                if self._stop_event.is_set():
                    break

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=settings.poll_interval_seconds,
                    )
                except TimeoutError:
                    continue

        except asyncio.CancelledError:
            logger.info("ARGOS polling worker was cancelled.")
            raise

        finally:
            self.state.is_running = False

            logger.info("ARGOS polling worker stopped.")

    async def _run_cycle(self) -> None:
        """Execute and record one polling cycle."""

        self.state.last_started_at = datetime.now(timezone.utc)

        try:
            summary = await poll_all_routers_once()

            self.state.last_summary = summary
            self.state.last_error = None

            logger.info(
                (
                    "Router polling completed: "
                    "total=%s online=%s offline=%s errors=%s"
                ),
                summary.total,
                summary.online,
                summary.offline,
                summary.errors,
            )

        except asyncio.CancelledError:
            raise

        except Exception:
            self.state.last_error = "Polling cycle failed."

            logger.exception(
                "Unexpected failure during router polling cycle."
            )

        finally:
            self.state.last_finished_at = datetime.now(timezone.utc)


polling_worker = PollingWorker()