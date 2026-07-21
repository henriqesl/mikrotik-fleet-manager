"""Scheduling policies used by the ARGOS polling worker."""

from datetime import datetime, timedelta


_FAILURE_BACKOFF_MULTIPLIERS = (1, 2, 5, 15)


def calculate_poll_delay_seconds(
    *,
    poll_interval_seconds: int,
    consecutive_failures: int,
    max_backoff_seconds: int,
) -> int:
    """Return the delay before the next polling attempt."""

    if poll_interval_seconds <= 0:
        raise ValueError("poll_interval_seconds must be positive.")

    if consecutive_failures < 0:
        raise ValueError("consecutive_failures cannot be negative.")

    if max_backoff_seconds <= 0:
        raise ValueError("max_backoff_seconds must be positive.")

    if consecutive_failures == 0:
        return poll_interval_seconds

    multiplier_index = min(
        consecutive_failures - 1,
        len(_FAILURE_BACKOFF_MULTIPLIERS) - 1,
    )
    multiplier = _FAILURE_BACKOFF_MULTIPLIERS[multiplier_index]

    effective_max_backoff = max(
        poll_interval_seconds,
        max_backoff_seconds,
    )

    return min(
        poll_interval_seconds * multiplier,
        effective_max_backoff,
    )


def calculate_initial_stagger_seconds(
    *,
    router_id: int,
    stagger_window_seconds: int,
) -> int:
    """Distribute initial router polls across a stable time window."""

    if router_id <= 0:
        raise ValueError("router_id must be positive.")

    if stagger_window_seconds < 0:
        raise ValueError("stagger_window_seconds cannot be negative.")

    if stagger_window_seconds == 0:
        return 0

    return (router_id * 37) % stagger_window_seconds


def calculate_initial_poll_at(
    *,
    now: datetime,
    router_id: int,
    stagger_window_seconds: int,
) -> datetime:
    """Return the first scheduled polling time for a router."""

    _ensure_timezone_aware(now)

    stagger_seconds = calculate_initial_stagger_seconds(
        router_id=router_id,
        stagger_window_seconds=stagger_window_seconds,
    )

    return now + timedelta(seconds=stagger_seconds)


def calculate_next_poll_at(
    *,
    finished_at: datetime,
    poll_interval_seconds: int,
    consecutive_failures: int,
    max_backoff_seconds: int,
) -> datetime:
    """Return the next polling time after a completed attempt."""

    _ensure_timezone_aware(finished_at)

    delay_seconds = calculate_poll_delay_seconds(
        poll_interval_seconds=poll_interval_seconds,
        consecutive_failures=consecutive_failures,
        max_backoff_seconds=max_backoff_seconds,
    )

    return finished_at + timedelta(seconds=delay_seconds)


def _ensure_timezone_aware(value: datetime) -> None:
    """Reject naive datetimes before they reach the database."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("A timezone-aware datetime is required.")