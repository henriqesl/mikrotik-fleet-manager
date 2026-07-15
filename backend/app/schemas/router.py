from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
)

from app.core.network_policy import (
    normalize_management_ip,
    normalize_optional_ip,
    validate_router_api_port,
)


class RouterStatus(str, Enum):
    """Possible monitoring states for a router."""

    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class RouterCreate(BaseModel):
    """Data required to register a new router."""

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Matriz"],
    )

    management_ip: str = Field(
        examples=["10.200.0.21"],
    )

    public_ip: str | None = Field(
        default=None,
        examples=["203.0.113.10"],
    )

    api_port: int = Field(
        default=8729,
        ge=1,
        le=65535,
    )

    username: str = Field(
        min_length=1,
        max_length=100,
        examples=["argos-api"],
    )

    password: SecretStr

    @field_validator("name", "username")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        """Remove surrounding whitespace from required text fields."""

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Value cannot be empty.")

        return normalized_value

    @field_validator("management_ip")
    @classmethod
    def validate_management_ip(cls, value: str) -> str:
        """Validate the router WireGuard management address."""

        return normalize_management_ip(value)

    @field_validator("public_ip")
    @classmethod
    def validate_public_ip(
        cls,
        value: str | None,
    ) -> str | None:
        """Validate the optional public inventory address."""

        return normalize_optional_ip(value)

    @field_validator("api_port")
    @classmethod
    def validate_api_port(cls, value: int) -> int:
        """Ensure the API port is allowed by policy."""

        return validate_router_api_port(value)


class RouterResponse(BaseModel):
    """Public representation of a registered router."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    management_ip: str
    public_ip: str | None
    api_port: int
    use_ssl: bool
    is_active: bool

    model: str | None
    identity: str | None
    routeros_version: str | None

    status: RouterStatus

    cpu_usage_percent: float | None
    memory_usage_percent: float | None
    uptime_seconds: int | None

    last_checked_at: datetime | None
    last_seen_at: datetime | None
    last_error: str | None

    created_at: datetime
    updated_at: datetime

class RouterListResponse(BaseModel):
    """Paginated list of registered routers."""

    items: list[RouterResponse]
    total: int
    offset: int
    limit: int