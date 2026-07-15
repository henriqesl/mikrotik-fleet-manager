"""create routers table

Revision ID: f8c99f2d4ec0
Revises: 
Create Date: 2026-07-15 09:53:29.381195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8c99f2d4ec0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "routers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("ip", sa.String(length=255), nullable=False),
        sa.Column(
            "api_port",
            sa.Integer(),
            server_default="8728",
            nullable=False,
        ),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column(
            "password_ciphertext",
            sa.String(length=512),
            nullable=False,
        ),
        sa.Column(
            "use_ssl",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("identity", sa.String(length=100), nullable=True),
        sa.Column(
            "routeros_version",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("cpu_usage_percent", sa.Float(), nullable=True),
        sa.Column("memory_usage_percent", sa.Float(), nullable=True),
        sa.Column("uptime_seconds", sa.BigInteger(), nullable=True),
        sa.Column(
            "last_checked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_routers"),
        ),
        sa.UniqueConstraint(
            "ip",
            name=op.f("uq_routers_ip"),
        ),
    )

    op.create_index(
        op.f("ix_routers_is_active"),
        "routers",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        op.f("ix_routers_name"),
        "routers",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_routers_status"),
        "routers",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_routers_status"),
        table_name="routers",
    )

    op.drop_index(
        op.f("ix_routers_name"),
        table_name="routers",
    )

    op.drop_index(
        op.f("ix_routers_is_active"),
        table_name="routers",
    )

    op.drop_table("routers")
