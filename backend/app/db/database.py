from collections.abc import AsyncGenerator

from typing import Any

from sqlalchemy import MetaData, text, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": (
        "fk_%(table_name)s_%(column_0_name)s_"
        "%(referred_table_name)s"
    ),
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

def _configure_sqlite_connection(
    dbapi_connection: Any,
    _: Any,
) -> None:
    """Configure SQLite for concurrent API and poller access."""

    cursor = dbapi_connection.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute(
            f"PRAGMA busy_timeout="
            f"{settings.sqlite_busy_timeout_ms}"
        )

        if settings.sqlite_wal_enabled:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")

    finally:
        cursor.close()


if settings.database_url.startswith("sqlite"):
    event.listen(
        engine.sync_engine,
        "connect",
        _configure_sqlite_connection,
    )


AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_database_session() -> AsyncGenerator[AsyncSession]:
    """Provide a database session for a single request."""

    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_connection() -> None:
    """Execute a simple query to verify database availability."""

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_database_connection() -> None:
    """Dispose of the database connection pool."""

    await engine.dispose()