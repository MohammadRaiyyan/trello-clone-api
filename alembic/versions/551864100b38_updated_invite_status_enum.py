"""Updated invite status enum

Revision ID: 551864100b38
Revises: 3e3d6bcd9ed5
"""

from typing import Sequence, Union

from alembic import op

revision: str = "551864100b38"
down_revision: Union[str, Sequence[str], None] = "3e3d6bcd9ed5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE invite_status_type ADD VALUE 'REVOKED'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing an individual ENUM value.
    pass
