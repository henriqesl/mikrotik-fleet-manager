from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_database_session
from app.repositories.router import RouterRepository
from app.schemas.router import RouterListResponse


router = APIRouter(
    prefix="/routers",
    tags=["Routers"],
)


@router.get(
    "",
    response_model=RouterListResponse,
)
async def list_routers(
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
) -> RouterListResponse:
    """Return a paginated list of registered routers."""

    repository = RouterRepository(session)

    routers = await repository.list_routers(
        offset=offset,
        limit=limit,
    )

    total = await repository.count_routers()

    return RouterListResponse(
        items=routers,
        total=total,
        offset=offset,
        limit=limit,
    )