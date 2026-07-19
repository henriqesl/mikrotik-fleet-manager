from datetime import datetime, timezone

from app.services.polling import (
    RouterPollingResult,
    build_polling_summary,
)


def test_builds_polling_summary() -> None:
    checked_at = datetime.now(timezone.utc)

    results = [
        RouterPollingResult(
            router_id=1,
            status="online",
            checked_at=checked_at,
        ),
        RouterPollingResult(
            router_id=2,
            status="online",
            checked_at=checked_at,
        ),
        RouterPollingResult(
            router_id=3,
            status="offline",
            checked_at=checked_at,
        ),
        RouterPollingResult(
            router_id=4,
            status="error",
            checked_at=checked_at,
        ),
    ]

    summary = build_polling_summary(results)

    assert summary.total == 4
    assert summary.online == 2
    assert summary.offline == 1
    assert summary.errors == 1