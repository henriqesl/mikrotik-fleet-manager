from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router


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