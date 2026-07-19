import pytest
from pydantic import ValidationError

from app.schemas.router import RouterCreate


def test_router_create_normalizes_input() -> None:
    router = RouterCreate(
        name=" Matriz ",
        management_ip="10.200.0.21",
        api_port=8729,
        username=" argos-api ",
        password="SecurePassword123!",
    )

    assert router.name == "Matriz"
    assert router.username == "argos-api"
    assert router.management_ip == "10.200.0.21"


def test_router_create_hides_password() -> None:
    router = RouterCreate(
        name="Matriz",
        management_ip="10.200.0.21",
        username="argos-api",
        password="SecurePassword123!",
    )

    assert "SecurePassword123!" not in repr(router)


def test_router_create_rejects_invalid_management_ip() -> None:
    with pytest.raises(ValidationError):
        RouterCreate(
            name="Matriz",
            management_ip="127.0.0.1",
            username="argos-api",
            password="SecurePassword123!",
        )