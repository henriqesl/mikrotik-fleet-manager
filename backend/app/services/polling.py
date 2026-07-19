import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.core.credential_cipher import (
    CredentialDecryptionError,
    get_credential_cipher,
)
from app.db.database import AsyncSessionFactory
from app.repositories.router import RouterRepository
from app.services.routeros import (
    RouterOSConnectionError,
    RouterOSDataError,
    RouterOSIntegrationError,
    RouterOSTLSConfigurationError,
    RouterSnapshot,
    collect_router_snapshot,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RouterPollingTarget:
    """Router connection data required by a polling task."""

    router_id: int
    management_ip: str
    api_port: int
    username: str
    password_ciphertext: str


@dataclass(frozen=True, slots=True)
class RouterPollingResult:
    """Result produced after checking a single router."""

    router_id: int
    status: str
    checked_at: datetime
    snapshot: RouterSnapshot | None = None
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class PollingCycleSummary:
    """Summary of a complete router polling cycle."""

    total: int
    online: int
    offline: int
    errors: int


async def load_polling_targets() -> list[RouterPollingTarget]:
    """Load active routers without keeping the session open."""

    async with AsyncSessionFactory() as session:
        repository = RouterRepository(session)

        routers = await repository.list_active_routers()

        return [
            RouterPollingTarget(
                router_id=router.id,
                management_ip=router.management_ip,
                api_port=router.api_port,
                username=router.username,
                password_ciphertext=router.password_ciphertext,
            )
            for router in routers
        ]


async def poll_router(
    target: RouterPollingTarget,
    semaphore: asyncio.Semaphore,
) -> RouterPollingResult:
    """Collect monitoring data from one router."""

    async with semaphore:
        checked_at = datetime.now(timezone.utc)

        try:
            credential_cipher = get_credential_cipher()

            password = credential_cipher.decrypt(
                target.password_ciphertext
            )

            snapshot = await collect_router_snapshot(
                management_ip=target.management_ip,
                api_port=target.api_port,
                username=target.username,
                password=password,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="online",
                checked_at=snapshot.checked_at,
                snapshot=snapshot,
                last_error=None,
            )

        except RouterOSConnectionError:
            return RouterPollingResult(
                router_id=target.router_id,
                status="offline",
                checked_at=checked_at,
                last_error="RouterOS connection failed.",
            )

        except CredentialDecryptionError:
            logger.exception(
                "Unable to decrypt credentials for router %s.",
                target.router_id,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="error",
                checked_at=checked_at,
                last_error="Credential decryption failed.",
            )

        except RouterOSTLSConfigurationError:
            logger.exception(
                "RouterOS TLS configuration failed for router %s.",
                target.router_id,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="error",
                checked_at=checked_at,
                last_error="RouterOS TLS trust is not configured.",
            )

        except RouterOSDataError:
            logger.exception(
                "Invalid RouterOS data received from router %s.",
                target.router_id,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="error",
                checked_at=checked_at,
                last_error="RouterOS returned invalid monitoring data.",
            )

        except RouterOSIntegrationError:
            logger.exception(
                "RouterOS integration failed for router %s.",
                target.router_id,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="error",
                checked_at=checked_at,
                last_error="RouterOS integration failed.",
            )

        except Exception:
            logger.exception(
                "Unexpected polling failure for router %s.",
                target.router_id,
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status="error",
                checked_at=checked_at,
                last_error="Unexpected monitoring failure.",
            )


async def persist_polling_results(
    results: list[RouterPollingResult],
) -> None:
    """Persist polling results using a single database transaction."""

    async with AsyncSessionFactory() as session:
        repository = RouterRepository(session)

        try:
            for result in results:
                router = await repository.get_by_id(
                    result.router_id
                )

                if router is None or not router.is_active:
                    continue

                updates: dict[str, object] = {
                    "status": result.status,
                    "last_checked_at": result.checked_at,
                    "last_error": result.last_error,
                }

                if result.snapshot is not None:
                    updates.update(
                        {
                            "model": result.snapshot.model,
                            "identity": result.snapshot.identity,
                            "routeros_version": (
                                result.snapshot.routeros_version
                            ),
                            "cpu_usage_percent": (
                                result.snapshot.cpu_usage_percent
                            ),
                            "memory_usage_percent": (
                                result.snapshot.memory_usage_percent
                            ),
                            "uptime_seconds": (
                                result.snapshot.uptime_seconds
                            ),
                            "last_seen_at": result.snapshot.checked_at,
                        }
                    )

                await repository.update_router(
                    router,
                    updates,
                )

            await session.commit()

        except Exception:
            await session.rollback()

            logger.exception(
                "Unable to persist router polling results."
            )

            raise


def build_polling_summary(
    results: list[RouterPollingResult],
) -> PollingCycleSummary:
    """Build aggregate counters for a polling cycle."""

    return PollingCycleSummary(
        total=len(results),
        online=sum(
            result.status == "online"
            for result in results
        ),
        offline=sum(
            result.status == "offline"
            for result in results
        ),
        errors=sum(
            result.status == "error"
            for result in results
        ),
    )


async def poll_all_routers_once() -> PollingCycleSummary:
    """Run one concurrent monitoring cycle for all active routers."""

    targets = await load_polling_targets()

    if not targets:
        return PollingCycleSummary(
            total=0,
            online=0,
            offline=0,
            errors=0,
        )

    semaphore = asyncio.Semaphore(
        settings.max_concurrent_router_checks
    )

    results = await asyncio.gather(
        *(
            poll_router(
                target,
                semaphore,
            )
            for target in targets
        )
    )

    await persist_polling_results(results)

    return build_polling_summary(results)