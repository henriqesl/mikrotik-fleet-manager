"""Tests for polling scheduling and retry policies."""

from datetime import datetime, timezone

import pytest

from app.polling.policies import (
    calculate_initial_poll_at,
    calculate_initial_stagger_seconds,
    calculate_next_poll_at,
    calculate_poll_delay_seconds,
)


def test_success_uses_normal_poll_interval() -> None:
    assert calculate_poll_delay_seconds(
        poll_interval_seconds=60,
        consecutive_failures=0,
        max_backoff_seconds=900,
    ) == 60


@pytest.mark.parametrize(
    ("consecutive_failures", "expected_delay"),
    [
        (1, 60),
        (2, 120),
        (3, 300),
        (4, 900),
        (10, 900),
    ],
)
def test_failure_delay_uses_backoff(
    consecutive_failures: int,
    expected_delay: int,
) -> None:
    assert calculate_poll_delay_seconds(
        poll_interval_seconds=60,
        consecutive_failures=consecutive_failures,
        max_backoff_seconds=900,
    ) == expected_delay


def test_backoff_respects_custom_maximum() -> None:
    assert calculate_poll_delay_seconds(
        poll_interval_seconds=60,
        consecutive_failures=10,
        max_backoff_seconds=300,
    ) == 300


def test_initial_stagger_is_stable_and_bounded() -> None:
    first_value = calculate_initial_stagger_seconds(
        router_id=123,
        stagger_window_seconds=60,
    )
    second_value = calculate_initial_stagger_seconds(
        router_id=123,
        stagger_window_seconds=60,
    )

    assert first_value == second_value
    assert 0 <= first_value < 60


def test_initial_poll_uses_router_stagger() -> None:
    now = datetime(
        2026,
        7,
        21,
        14,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_initial_poll_at(
        now=now,
        router_id=1,
        stagger_window_seconds=60,
    )

    assert result == datetime(
        2026,
        7,
        21,
        14,
        0,
        37,
        tzinfo=timezone.utc,
    )


def test_next_poll_uses_failure_backoff() -> None:
    finished_at = datetime(
        2026,
        7,
        21,
        14,
        0,
        tzinfo=timezone.utc,
    )

    result = calculate_next_poll_at(
        finished_at=finished_at,
        poll_interval_seconds=60,
        consecutive_failures=3,
        max_backoff_seconds=900,
    )

    assert result == datetime(
        2026,
        7,
        21,
        14,
        5,
        tzinfo=timezone.utc,
    )


def test_rejects_naive_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        calculate_initial_poll_at(
            now=datetime(2026, 7, 21, 14, 0),
            router_id=1,
            stagger_window_seconds=60,
        )