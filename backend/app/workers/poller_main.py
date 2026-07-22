"""Standalone entrypoint for the ARGOS polling worker."""

import asyncio
import logging

from app.core.config import settings
from app.core.credential_cipher import get_credential_cipher
from app.core.logging import configure_logging
from app.db.database import (
    check_database_connection,
    close_database_connection,
)

from app.workers.polling import polling_worker
from app.services.polling import initialize_polling_schedule

logger = logging.getLogger(__name__)


async def run_poller() -> None:
    """Run the polling scheduler as an independent process."""

    configure_logging()
    get_credential_cipher()

    await check_database_connection()

    if not settings.polling_enabled:
        logger.warning(
            "ARGOS standalone polling worker is disabled."
        )
        await close_database_connection()
        return

    logger.info(
        "Starting ARGOS standalone polling worker."
    )

    initialized_routers = await initialize_polling_schedule()

    logger.info(
        "Initialized polling schedule for %s router(s).",
        initialized_routers,
    )

    polling_worker.start()

    try:
        # Remain alive until the process receives Ctrl+C or is stopped.
        await asyncio.Future()
    finally:
        logger.info(
            "Stopping ARGOS standalone polling worker."
        )
        await polling_worker.stop()
        await close_database_connection()


def main() -> None:
    """Start the standalone polling process."""

    try:
        asyncio.run(run_poller())
    except KeyboardInterrupt:
        logger.info(
            "ARGOS standalone polling worker interrupted."
        )


if __name__ == "__main__":
    main()