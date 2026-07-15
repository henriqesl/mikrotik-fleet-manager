from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
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