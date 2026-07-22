"""Deterministic environment used by the backend test suite."""

import os

import pytest

# Environment variables take precedence over values loaded from .env.
# Tests must not depend on the developer's current WireGuard network.
os.environ["MANAGEMENT_NETWORKS"] = '["10.200.0.0/24"]'
os.environ["ALLOWED_ROUTER_API_PORTS"] = "[8729]"

@pytest.fixture
def anyio_backend() -> str:
    """Run asynchronous tests using asyncio only."""

    return "asyncio"