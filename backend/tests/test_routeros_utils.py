import pytest

from app.services.routeros import (
    RouterOSDataError,
    calculate_memory_usage_percent,
    parse_uptime_seconds,
)


def test_parses_routeros_uptime() -> None:
    assert parse_uptime_seconds(
        "1w2d3h4m5s"
    ) == 788645


def test_rejects_invalid_routeros_uptime() -> None:
    with pytest.raises(RouterOSDataError):
        parse_uptime_seconds("invalid")


def test_calculates_memory_usage() -> None:
    result = calculate_memory_usage_percent(
        total_memory=1000,
        free_memory=250,
    )

    assert result == 75.0


def test_returns_none_for_invalid_total_memory() -> None:
    assert calculate_memory_usage_percent(
        total_memory=0,
        free_memory=0,
    ) is None