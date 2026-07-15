from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router

from datetime import datetime

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