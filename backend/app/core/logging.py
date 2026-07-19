import logging

from app.core.config import settings


VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def configure_logging() -> None:
    """Configure application logging."""

    log_level = settings.log_level.upper()

    if log_level not in VALID_LOG_LEVELS:
        log_level = "INFO"

    logging.getLogger("app").setLevel(log_level)

    sqlalchemy_level = (
        logging.INFO
        if settings.debug
        else logging.WARNING
    )

    logging.getLogger("sqlalchemy.engine").setLevel(
        sqlalchemy_level
    )