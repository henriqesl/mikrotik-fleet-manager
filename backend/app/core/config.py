from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import SecretStr

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "ARGOS API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = "sqlite+aiosqlite:///./argos.db"

    routeros_ca_file: str = "certs/routeros-ca.pem"
    routeros_socket_timeout_seconds: float = 5.0

    cors_origins: list[str] = [
        "http://localhost:5173",
    ]

    management_networks: list[str] = [
        "10.200.0.0/16",
    ]

    allowed_router_api_ports: list[int] = [
        8729,
    ]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    credential_encryption_key: SecretStr


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()


settings = get_settings()