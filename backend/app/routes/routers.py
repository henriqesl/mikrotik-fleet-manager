from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credential_cipher import (
    CredentialCipher,
    get_credential_cipher,
)
from app.db.database import get_database_session
from app.repositories.router import RouterRepository
from app.schemas.router import (
    RouterCreate,
    RouterListResponse,
    RouterResponse,
)
from app.services.routeros import (
    RouterOSConnectionError,
    RouterOSDataError,
    RouterOSTLSConfigurationError,
    collect_router_snapshot,
)


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


@router.get(
    "/{router_id}",
    response_model=RouterResponse,
)
async def get_router(
    router_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
) -> RouterResponse:
    """Return the details of a registered router."""

    repository = RouterRepository(session)

    router_record = await repository.get_by_id(router_id)

    if router_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found.",
        )

    return RouterResponse.model_validate(router_record)


@router.post(
    "",
    response_model=RouterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_router(
    payload: RouterCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
    credential_cipher: Annotated[
        CredentialCipher,
        Depends(get_credential_cipher),
    ],
) -> RouterResponse:
    """Validate and register a router with encrypted credentials."""

    repository = RouterRepository(session)

    existing_router = await repository.get_by_management_ip(
        payload.management_ip
    )

    if existing_router is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A router with this management IP "
                "is already registered."
            ),
        )

    plaintext_password = payload.password.get_secret_value()

    try:
        router_snapshot = await collect_router_snapshot(
            management_ip=payload.management_ip,
            api_port=payload.api_port,
            username=payload.username,
            password=plaintext_password,
        )

    except RouterOSTLSConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "RouterOS TLS trust is not configured "
                "on the ARGOS server."
            ),
        ) from exc

    except (RouterOSConnectionError, RouterOSDataError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "ARGOS could not establish a trusted "
                "RouterOS API connection."
            ),
        ) from exc

    password_ciphertext = credential_cipher.encrypt(
        plaintext_password
    )

    try:
        router_record = await repository.create_router(
            name=payload.name,
            management_ip=payload.management_ip,
            public_ip=payload.public_ip,
            api_port=payload.api_port,
            username=payload.username,
            password_ciphertext=password_ciphertext,
            model=router_snapshot.model,
            identity=router_snapshot.identity,
            routeros_version=router_snapshot.routeros_version,
            cpu_usage_percent=router_snapshot.cpu_usage_percent,
            memory_usage_percent=(
                router_snapshot.memory_usage_percent
            ),
            uptime_seconds=router_snapshot.uptime_seconds,
            checked_at=router_snapshot.checked_at,
        )

        await session.commit()
        await session.refresh(router_record)

    except IntegrityError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A router with this management IP "
                "is already registered."
            ),
        ) from exc

    return RouterResponse.model_validate(router_record)