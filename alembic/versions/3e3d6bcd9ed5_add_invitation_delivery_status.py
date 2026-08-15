"""Add invitation delivery status

Revision ID: 3e3d6bcd9ed5
Revises: 06c80c28f804
Create Date: 2026-08-15 15:33:19.340204

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3e3d6bcd9ed5"
down_revision: Union[str, Sequence[str], None] = "06c80c28f804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    delivery_status_type = sa.Enum(
        "PENDING",
        "SENT",
        "FAILED",
        name="invitation_delivery_status_type",
    )

    delivery_status_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "organization_invites",
        sa.Column(
            "delivery_status",
            delivery_status_type,
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.alter_column(
        "organization_invites",
        "delivery_status",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "organization_invites",
        "delivery_status",
    )

    delivery_status_type = sa.Enum(
        "PENDING",
        "SENT",
        "FAILED",
        name="invitation_delivery_status_type",
    )

    delivery_status_type.drop(op.get_bind(), checkfirst=True)
