from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Router(Base):
    """Represent a MikroTik router managed by ARGOS."""

    __tablename__ = "routers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    management_ip: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    public_ip: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    api_port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8729,
        server_default="8729",
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    password_ciphertext: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    use_ssl: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
        index=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    identity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    routeros_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="unknown",
        server_default="unknown",
        index=True,
    )

    cpu_usage_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    memory_usage_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    uptime_seconds: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"Router(id={self.id!r}, "
            f"name={self.name!r}, "
            f"management_ip={self.management_ip!r})"
        )