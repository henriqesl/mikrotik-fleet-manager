"""Scheduled and concurrent RouterOS polling services."""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import settings
from app.core.credential_cipher import (
    CredentialDecryptionError,
    get_credential_cipher,
)
from app.db.database import AsyncSessionFactory
from app.polling.policies import (
    calculate_initial_poll_at,
    calculate_next_poll_at,
)
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
    finished_at: datetime
    duration_ms: int
    snapshot: RouterSnapshot | None = None
    last_error: str | None = None
    last_error_code: str | None = None


@dataclass(frozen=True, slots=True)
class PollingCycleSummary:
    """Summary of a scheduled polling batch."""

    total: int
    online: int
    offline: int
    errors: int


async def initialize_polling_schedule(
    *,
    now: datetime | None = None,
) -> int:
    """Assign an initial staggered polling time to new routers."""

    schedule_now = now or datetime.now(timezone.utc)

    async with AsyncSessionFactory() as session:
        repository = RouterRepository(session)
        routers = await repository.list_unscheduled_active_routers()

        try:
            for router in routers:
                router.next_poll_at = calculate_initial_poll_at(
                    now=schedule_now,
                    router_id=router.id,
                    stagger_window_seconds=(
                        settings.poll_initial_stagger_seconds
                    ),
                )

            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception(
                "Unable to initialize router polling schedules."
            )
            raise

    return len(routers)


async def reserve_due_polling_targets(
    *,
    worker_id: str,
    now: datetime | None = None,
) -> list[RouterPollingTarget]:
    """Atomically reserve one batch of routers for polling."""

    lease_started_at = now or datetime.now(timezone.utc)
    lease_until = lease_started_at + timedelta(
        seconds=settings.poll_lease_seconds
    )

    async with AsyncSessionFactory() as session:
        repository = RouterRepository(session)

        try:
            routers = await repository.reserve_due_routers(
                worker_id=worker_id,
                now=lease_started_at,
                lease_until=lease_until,
                limit=settings.poll_batch_size,
            )

            targets = [
                RouterPollingTarget(
                    router_id=router.id,
                    management_ip=router.management_ip,
                    api_port=router.api_port,
                    username=router.username,
                    password_ciphertext=(
                        router.password_ciphertext
                    ),
                )
                for router in routers
            ]

            await session.commit()
            return targets

        except Exception:
            await session.rollback()
            logger.exception(
                "Unable to reserve routers for polling."
            )
            raise


async def poll_router(
    target: RouterPollingTarget,
    semaphore: asyncio.Semaphore,
) -> RouterPollingResult:
    """Collect monitoring data from one router."""

    async with semaphore:
        started_at = datetime.now(timezone.utc)
        started_counter = time.perf_counter()

        def build_result(
            *,
            status: str,
            snapshot: RouterSnapshot | None = None,
            last_error: str | None = None,
            last_error_code: str | None = None,
        ) -> RouterPollingResult:
            finished_at = datetime.now(timezone.utc)
            duration_ms = max(
                0,
                round(
                    (time.perf_counter() - started_counter)
                    * 1000
                ),
            )

            return RouterPollingResult(
                router_id=target.router_id,
                status=status,
                checked_at=(
                    snapshot.checked_at
                    if snapshot is not None
                    else started_at
                ),
                finished_at=finished_at,
                duration_ms=duration_ms,
                snapshot=snapshot,
                last_error=last_error,
                last_error_code=last_error_code,
            )

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

            return build_result(
                status="online",
                snapshot=snapshot,
            )

        except RouterOSConnectionError:
            return build_result(
                status="offline",
                last_error="RouterOS connection failed.",
                last_error_code="connection_failed",
            )

        except CredentialDecryptionError:
            logger.exception(
                "Unable to decrypt credentials for router %s.",
                target.router_id,
            )
            return build_result(
                status="error",
                last_error="Credential decryption failed.",
                last_error_code="credential_decryption_failed",
            )

        except RouterOSTLSConfigurationError:
            logger.exception(
                "RouterOS TLS configuration failed for router %s.",
                target.router_id,
            )
            return build_result(
                status="error",
                last_error="RouterOS TLS trust is not configured.",
                last_error_code="tls_configuration_failed",
            )

        except RouterOSDataError:
            logger.exception(
                "Invalid RouterOS data received from router %s.",
                target.router_id,
            )
            return build_result(
                status="error",
                last_error=(
                    "RouterOS returned invalid monitoring data."
                ),
                last_error_code="invalid_routeros_data",
            )

        except RouterOSIntegrationError:
            logger.exception(
                "RouterOS integration failed for router %s.",
                target.router_id,
            )
            return build_result(
                status="error",
                last_error="RouterOS integration failed.",
                last_error_code="routeros_integration_failed",
            )

        except Exception:
            logger.exception(
                "Unexpected polling failure for router %s.",
                target.router_id,
            )
            return build_result(
                status="error",
                last_error="Unexpected monitoring failure.",
                last_error_code="unexpected_error",
            )


async def persist_polling_results(
    results: list[RouterPollingResult],
    *,
    worker_id: str,
) -> None:
    """Persist polling results and release their polling leases."""

    async with AsyncSessionFactory() as session:
        repository = RouterRepository(session)

        try:
            for result in results:
                router = await repository.get_by_id(
                    result.router_id
                )

                if router is None:
                    continue

                if router.poll_lease_owner != worker_id:
                    logger.warning(
                        "Ignoring stale polling result for router %s.",
                        result.router_id,
                    )
                    continue

                if result.status == "online":
                    consecutive_failures = 0
                else:
                    consecutive_failures = (
                        router.consecutive_failures + 1
                    )

                updates: dict[str, object] = {
                    "status": result.status,
                    "last_checked_at": result.checked_at,
                    "last_error": result.last_error,
                    "last_error_code": result.last_error_code,
                    "last_poll_finished_at": result.finished_at,
                    "poll_duration_ms": result.duration_ms,
                    "consecutive_failures": consecutive_failures,
                    "next_poll_at": calculate_next_poll_at(
                        finished_at=result.finished_at,
                        poll_interval_seconds=(
                            settings.poll_interval_seconds
                        ),
                        consecutive_failures=(
                            consecutive_failures
                        ),
                        max_backoff_seconds=(
                            settings.poll_max_backoff_seconds
                        ),
                    ),
                    "poll_lease_until": None,
                    "poll_lease_owner": None,
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
                            "last_seen_at": (
                                result.snapshot.checked_at
                            ),
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
    """Build aggregate counters for a polling batch."""

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


async def poll_due_routers_once() -> PollingCycleSummary:
    """Poll one scheduled batch of due routers."""

    worker_id = f"poller-{uuid4()}"
    targets = await reserve_due_polling_targets(
        worker_id=worker_id,
    )

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

    await persist_polling_results(
        results,
        worker_id=worker_id,
    )

    return build_polling_summary(results)


async def poll_all_routers_once() -> PollingCycleSummary:
    """Backward-compatible alias for one scheduled polling batch."""

    return await poll_due_routers_once()