import pytest

from app.core.network_policy import (
    normalize_management_ip,
    normalize_optional_ip,
    validate_router_api_port,
)


def test_accepts_management_ip_inside_allowed_network() -> None:
    assert normalize_management_ip(
        "10.200.0.21"
    ) == "10.200.0.21"


def test_rejects_management_ip_outside_allowed_network() -> None:
    with pytest.raises(ValueError):
        normalize_management_ip("127.0.0.1")


def test_normalizes_optional_public_ip() -> None:
    assert normalize_optional_ip(
        " 203.0.113.10 "
    ) == "203.0.113.10"


def test_accepts_empty_optional_public_ip() -> None:
    assert normalize_optional_ip("") is None
    assert normalize_optional_ip(None) is None


def test_rejects_unapproved_routeros_port() -> None:
    with pytest.raises(ValueError):
        validate_router_api_port(8728)


def test_accepts_approved_routeros_port() -> None:
    assert validate_router_api_port(8729) == 8729