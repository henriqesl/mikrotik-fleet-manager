from ipaddress import (
    IPv4Network,
    IPv6Network,
    ip_address,
    ip_network,
)

from app.core.config import settings


Network = IPv4Network | IPv6Network


def load_management_networks() -> tuple[Network, ...]:
    """Parse the configured WireGuard management networks."""

    try:
        return tuple(
            ip_network(network, strict=False)
            for network in settings.management_networks
        )
    except ValueError as exc:
        raise RuntimeError(
            "Invalid MANAGEMENT_NETWORKS configuration."
        ) from exc


MANAGEMENT_NETWORKS = load_management_networks()

ALLOWED_ROUTER_API_PORTS = frozenset(
    settings.allowed_router_api_ports
)


def normalize_management_ip(value: str) -> str:
    """Validate an IP and ensure it belongs to a management network."""

    normalized_value = value.strip()

    try:
        address = ip_address(normalized_value)
    except ValueError as exc:
        raise ValueError(
            "A valid management IPv4 or IPv6 address is required."
        ) from exc

    if not any(
        address in network
        for network in MANAGEMENT_NETWORKS
    ):
        raise ValueError(
            "The management IP is outside the allowed "
            "WireGuard networks."
        )

    return str(address)


def normalize_optional_ip(value: str | None) -> str | None:
    """Validate and normalize an optional inventory IP."""

    if value is None:
        return None

    normalized_value = value.strip()

    if not normalized_value:
        return None

    try:
        return str(ip_address(normalized_value))
    except ValueError as exc:
        raise ValueError(
            "A valid IPv4 or IPv6 address is required."
        ) from exc


def validate_router_api_port(value: int) -> int:
    """Ensure RouterOS connections use an approved API port."""

    if value not in ALLOWED_ROUTER_API_PORTS:
        raise ValueError(
            "The RouterOS API port is not allowed."
        )

    return value