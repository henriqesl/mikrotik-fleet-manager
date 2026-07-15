import asyncio
import re
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import routeros_api

from app.core.config import BACKEND_DIR, settings


UPTIME_UNIT_SECONDS = {
    "y": 365 * 24 * 60 * 60,
    "w": 7 * 24 * 60 * 60,
    "d": 24 * 60 * 60,
    "h": 60 * 60,
    "m": 60,
    "s": 1,
}

UPTIME_PART_PATTERN = re.compile(r"(\d+)([ywdhms])")


class RouterOSIntegrationError(RuntimeError):
    """Base error for RouterOS integration failures."""


class RouterOSTLSConfigurationError(RouterOSIntegrationError):
    """Raised when the local TLS trust configuration is invalid."""


class RouterOSConnectionError(RouterOSIntegrationError):
    """Raised when a trusted RouterOS connection cannot be established."""


class RouterOSDataError(RouterOSIntegrationError):
    """Raised when RouterOS returns missing or invalid information."""


@dataclass(frozen=True, slots=True)
class RouterSnapshot:
    """Current inventory and monitoring data collected from RouterOS."""

    model: str | None
    identity: str | None
    routeros_version: str | None
    cpu_usage_percent: float | None
    memory_usage_percent: float | None
    uptime_seconds: int | None
    checked_at: datetime


def resolve_ca_file() -> Path:
    """Resolve the configured RouterOS CA certificate path."""

    ca_file = Path(settings.routeros_ca_file)

    if not ca_file.is_absolute():
        ca_file = BACKEND_DIR / ca_file

    return ca_file.resolve()


def create_routeros_ssl_context() -> ssl.SSLContext:
    """Create a TLS context with certificate verification enabled."""

    ca_file = resolve_ca_file()

    if not ca_file.is_file():
        raise RouterOSTLSConfigurationError(
            "The RouterOS CA certificate file was not found."
        )

    try:
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(ca_file),
        )
    except (OSError, ssl.SSLError) as exc:
        raise RouterOSTLSConfigurationError(
            "Unable to load the RouterOS CA certificate."
        ) from exc

    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    return context


def parse_uptime_seconds(value: str | None) -> int | None:
    """Convert RouterOS uptime text into seconds."""

    if value is None:
        return None

    normalized_value = value.strip()

    if not normalized_value:
        return None

    total_seconds = 0
    current_position = 0

    for match in UPTIME_PART_PATTERN.finditer(normalized_value):
        if match.start() != current_position:
            raise RouterOSDataError(
                "RouterOS returned an invalid uptime value."
            )

        amount = int(match.group(1))
        unit = match.group(2)

        total_seconds += amount * UPTIME_UNIT_SECONDS[unit]
        current_position = match.end()

    if current_position == 0 or current_position != len(normalized_value):
        raise RouterOSDataError(
            "RouterOS returned an invalid uptime value."
        )

    return total_seconds


def optional_text(value: Any) -> str | None:
    """Normalize an optional RouterOS text value."""

    if value is None:
        return None

    normalized_value = str(value).strip()

    return normalized_value or None


def optional_float(value: Any) -> float | None:
    """Convert an optional RouterOS value to float."""

    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RouterOSDataError(
            "RouterOS returned an invalid numeric value."
        ) from exc


def optional_int(value: Any) -> int | None:
    """Convert an optional RouterOS value to integer."""

    if value is None or value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RouterOSDataError(
            "RouterOS returned an invalid integer value."
        ) from exc


def calculate_memory_usage_percent(
    total_memory: int | None,
    free_memory: int | None,
) -> float | None:
    """Calculate the percentage of memory currently in use."""

    if total_memory is None or free_memory is None:
        return None

    if total_memory <= 0:
        return None

    used_memory = total_memory - free_memory
    usage_percent = used_memory / total_memory * 100

    return round(
        min(max(usage_percent, 0.0), 100.0),
        2,
    )


def get_first_record(
    records: list[dict[str, Any]],
    resource_name: str,
) -> dict[str, Any]:
    """Return the first record from a required RouterOS resource."""

    if not records:
        raise RouterOSDataError(
            f"RouterOS returned no data for {resource_name}."
        )

    return records[0]


def collect_router_snapshot_sync(
    *,
    management_ip: str,
    api_port: int,
    username: str,
    password: str,
) -> RouterSnapshot:
    """Collect RouterOS information using the blocking API client."""

    connection = None

    try:
        ssl_context = create_routeros_ssl_context()

        connection = routeros_api.RouterOsApiPool(
            management_ip,
            username=username,
            password=password,
            port=api_port,
            plaintext_login=True,
            use_ssl=True,
            ssl_context=ssl_context,
        )

        connection.set_timeout(
            settings.routeros_socket_timeout_seconds
        )

        api = connection.get_api()

        identity_records = api.get_resource(
            "/system/identity"
        ).get()

        resource_records = api.get_resource(
            "/system/resource"
        ).get()

        identity_data = get_first_record(
            identity_records,
            "/system/identity",
        )

        resource_data = get_first_record(
            resource_records,
            "/system/resource",
        )

        total_memory = optional_int(
            resource_data.get("total-memory")
        )

        free_memory = optional_int(
            resource_data.get("free-memory")
        )

        return RouterSnapshot(
            model=optional_text(
                resource_data.get("board-name")
            ),
            identity=optional_text(
                identity_data.get("name")
            ),
            routeros_version=optional_text(
                resource_data.get("version")
            ),
            cpu_usage_percent=optional_float(
                resource_data.get("cpu-load")
            ),
            memory_usage_percent=calculate_memory_usage_percent(
                total_memory,
                free_memory,
            ),
            uptime_seconds=parse_uptime_seconds(
                optional_text(resource_data.get("uptime"))
            ),
            checked_at=datetime.now(timezone.utc),
        )

    except RouterOSIntegrationError:
        raise

    except ssl.SSLCertVerificationError as exc:
        raise RouterOSConnectionError(
            "RouterOS certificate verification failed."
        ) from exc

    except Exception as exc:
        raise RouterOSConnectionError(
            "Unable to communicate with RouterOS."
        ) from exc

    finally:
        if connection is not None:
            connection.disconnect()


async def collect_router_snapshot(
    *,
    management_ip: str,
    api_port: int,
    username: str,
    password: str,
) -> RouterSnapshot:
    """Collect RouterOS information without blocking the event loop."""

    return await asyncio.to_thread(
        collect_router_snapshot_sync,
        management_ip=management_ip,
        api_port=api_port,
        username=username,
        password=password,
    )