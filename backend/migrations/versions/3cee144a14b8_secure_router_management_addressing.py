"""secure router management addressing

Revision ID: 3cee144a14b8
Revises: f8c99f2d4ec0
Create Date: 2026-07-15 11:08:22.563143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cee144a14b8'
down_revision: Union[str, Sequence[str], None] = 'f8c99f2d4ec0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("routers", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_routers_ip",
            type_="unique",
        )

        batch_op.alter_column(
            "ip",
            new_column_name="management_ip",
            existing_type=sa.String(length=255),
            existing_nullable=False,
        )

        batch_op.add_column(
            sa.Column(
                "public_ip",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.alter_column(
            "api_port",
            existing_type=sa.Integer(),
            existing_nullable=False,
            server_default=sa.text("8729"),
        )

        batch_op.alter_column(
            "use_ssl",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            server_default=sa.text("1"),
        )

        batch_op.create_unique_constraint(
            "uq_routers_management_ip",
            ["management_ip"],
        )


def downgrade() -> None:
    with op.batch_alter_table("routers", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_routers_management_ip",
            type_="unique",
        )

        batch_op.drop_column("public_ip")

        batch_op.alter_column(
            "management_ip",
            new_column_name="ip",
            existing_type=sa.String(length=255),
            existing_nullable=False,
        )

        batch_op.alter_column(
            "api_port",
            existing_type=sa.Integer(),
            existing_nullable=False,
            server_default=sa.text("8728"),
        )

        batch_op.alter_column(
            "use_ssl",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            server_default=sa.text("0"),
        )

        batch_op.create_unique_constraint(
            "uq_routers_ip",
            ["ip"],
        )