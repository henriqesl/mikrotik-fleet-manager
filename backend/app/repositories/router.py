from datetime import datetime

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router

@dataclass(frozen=True, slots=True)
class PollingOverview:
    """Database-backed overview of the polling scheduler."""

    active_routers: int
    due_routers: int
    leased_routers: int
    last_started_at: datetime | None
    last_finished_at: datetime | None

class RouterRepository:
    """Handle database operations related to routers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_routers(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Router]:
        """Return routers ordered by name and ID."""

        statement = (
            select(Router)
            .order_by(
                Router.name.asc(),
                Router.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.scalars(statement)

        return list(result.all())

    async def count_routers(self) -> int:
        """Return the total number of registered routers."""

        statement = select(func.count()).select_from(Router)
        result = await self._session.scalar(statement)

        return result or 0

    async def get_by_management_ip(
        self,
        management_ip: str,
    ) -> Router | None:
        """Return a router by its management IP."""

        statement = select(Router).where(
            Router.management_ip == management_ip
        )

        return await self._session.scalar(statement)
    
    async def get_by_id(
        self,
        router_id: int,
    ) -> Router | None:
        """Return a router by its database ID."""

        statement = select(Router).where(
            Router.id == router_id
        )

        return await self._session.scalar(statement)

    async def create_router(
    self,
    *,
    name: str,
    management_ip: str,
    public_ip: str | None,
    api_port: int,
    username: str,
    password_ciphertext: str,
    model: str | None,
    identity: str | None,
    routeros_version: str | None,
    cpu_usage_percent: float | None,
    memory_usage_percent: float | None,
    uptime_seconds: int | None,
    checked_at: datetime,
    ) -> Router:
        """Create a validated router without committing the transaction."""

        router = Router(
            name=name,
            management_ip=management_ip,
            public_ip=public_ip,
            api_port=api_port,
            username=username,
            password_ciphertext=password_ciphertext,
            use_ssl=True,
            is_active=True,
            model=model,
            identity=identity,
            routeros_version=routeros_version,
            status="online",
            cpu_usage_percent=cpu_usage_percent,
            memory_usage_percent=memory_usage_percent,
            uptime_seconds=uptime_seconds,
            last_checked_at=checked_at,
            last_seen_at=checked_at,
            last_error=None,
        )

        self._session.add(router)
        await self._session.flush()

        return router
    
    async def update_router(
        self,
        router: Router,
        updates: dict[str, object],
    ) -> Router:
        """Apply validated changes without committing the transaction."""

        for field_name, field_value in updates.items():
            setattr(router, field_name, field_value)

        await self._session.flush()

        return router
    
    async def list_active_routers(self) -> list[Router]:
        """Return all routers enabled for automatic monitoring."""

        statement = (
            select(Router)
            .where(Router.is_active.is_(True))
            .order_by(Router.id.asc())
        )

        result = await self._session.scalars(statement)

        return list(result.all())
    

    async def list_unscheduled_active_routers(
        self,
    ) -> list[Router]:
        """Return active routers without an initial polling schedule."""

        statement = (
            select(Router)
            .where(
                Router.is_active.is_(True),
                Router.next_poll_at.is_(None),
            )
            .order_by(Router.id.asc())
        )

        result = await self._session.scalars(statement)

        return list(result.all())


    async def reserve_due_routers(
        self,
        *,
        worker_id: str,
        now: datetime,
        lease_until: datetime,
        limit: int,
    ) -> list[Router]:
        """Atomically reserve one batch of due routers."""

        candidate_ids = (
            select(Router.id)
            .where(
                Router.is_active.is_(True),
                Router.next_poll_at.is_not(None),
                Router.next_poll_at <= now,
                or_(
                    Router.poll_lease_until.is_(None),
                    Router.poll_lease_until <= now,
                ),
            )
            .order_by(
                Router.next_poll_at.asc(),
                Router.id.asc(),
            )
            .limit(limit)
        )

        statement = (
            update(Router)
            .where(
                Router.id.in_(candidate_ids),
                Router.is_active.is_(True),
                or_(
                    Router.poll_lease_until.is_(None),
                    Router.poll_lease_until <= now,
                ),
            )
            .values(
                poll_lease_owner=worker_id,
                poll_lease_until=lease_until,
                last_poll_started_at=now,
            )
            .returning(Router)
        )

        result = await self._session.scalars(
            statement,
            execution_options={
                "synchronize_session": False,
            },
        )

        return list(result.all())


    async def queue_all_active_routers(
        self,
        *,
        now: datetime,
    ) -> int:
        """Mark every available active router for immediate polling."""

        statement = (
            update(Router)
            .where(
                Router.is_active.is_(True),
                or_(
                    Router.poll_lease_until.is_(None),
                    Router.poll_lease_until <= now,
                ),
            )
            .values(next_poll_at=now)
        )

        result = await self._session.execute(statement)
        return int(result.rowcount or 0)

    async def queue_router_for_polling(
        self,
        *,
        router_id: int,
        now: datetime,
    ) -> str:
        """Request immediate polling for one router."""

        router = await self.get_by_id(router_id)

        if router is None:
            return "not_found"

        if not router.is_active:
            return "inactive"

        statement = (
            update(Router)
            .where(
                Router.id == router_id,
                Router.is_active.is_(True),
                or_(
                    Router.poll_lease_until.is_(None),
                    Router.poll_lease_until <= now,
                ),
            )
            .values(next_poll_at=now)
        )

        result = await self._session.execute(statement)

        if result.rowcount:
            return "queued"

        return "in_progress"

    async def get_polling_overview(
        self,
        *,
        now: datetime,
    ) -> PollingOverview:
        """Return scheduler information stored in the database."""

        active_routers = await self._session.scalar(
            select(func.count())
            .select_from(Router)
            .where(Router.is_active.is_(True))
        )

        due_routers = await self._session.scalar(
            select(func.count())
            .select_from(Router)
            .where(
                Router.is_active.is_(True),
                Router.next_poll_at.is_not(None),
                Router.next_poll_at <= now,
                or_(
                    Router.poll_lease_until.is_(None),
                    Router.poll_lease_until <= now,
                ),
            )
        )

        leased_routers = await self._session.scalar(
            select(func.count())
            .select_from(Router)
            .where(
                Router.is_active.is_(True),
                Router.poll_lease_until.is_not(None),
                Router.poll_lease_until > now,
            )
        )

        last_started_at = await self._session.scalar(
            select(func.max(Router.last_poll_started_at))
        )

        last_finished_at = await self._session.scalar(
            select(func.max(Router.last_poll_finished_at))
        )

        return PollingOverview(
            active_routers=int(active_routers or 0),
            due_routers=int(due_routers or 0),
            leased_routers=int(leased_routers or 0),
            last_started_at=last_started_at,
            last_finished_at=last_finished_at,
        )