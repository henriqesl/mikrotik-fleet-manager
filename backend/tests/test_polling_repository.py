"""Concurrency tests for scheduled router polling."""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.db.database import Base
from app.models.router import Router
from app.repositories.router import RouterRepository


@pytest.mark.anyio
async def test_workers_do_not_reserve_same_routers(
    tmp_path,
) -> None:
    """Concurrent workers must receive disjoint router batches."""

    database_path = tmp_path / "polling-test.db"
    database_url = (
        f"sqlite+aiosqlite:///{database_path.as_posix()}"
    )

    engine = create_async_engine(
        database_url,
        connect_args={"timeout": 5},
    )

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    now = datetime.now(timezone.utc)

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    async with session_factory() as session:
        session.add_all(
            [
                Router(
                    name=f"Router {index}",
                    management_ip=f"10.200.0.{index}",
                    api_port=8729,
                    username="argos-api",
                    password_ciphertext="encrypted",
                    use_ssl=True,
                    is_active=True,
                    status="unknown",
                    next_poll_at=(
                        now - timedelta(seconds=1)
                    ),
                )
                for index in range(1, 5)
            ]
        )

        await session.commit()

    async def reserve(
        worker_id: str,
    ) -> set[int]:
        async with session_factory() as session:
            repository = RouterRepository(session)

            routers = await repository.reserve_due_routers(
                worker_id=worker_id,
                now=now,
                lease_until=(
                    now + timedelta(seconds=120)
                ),
                limit=2,
            )

            router_ids = {
                router.id
                for router in routers
            }

            await session.commit()
            return router_ids

    try:
        first_batch, second_batch = await asyncio.gather(
            reserve("worker-a"),
            reserve("worker-b"),
        )

        assert len(first_batch) == 2
        assert len(second_batch) == 2
        assert first_batch.isdisjoint(second_batch)
        assert len(first_batch | second_batch) == 4

    finally:
        await engine.dispose()