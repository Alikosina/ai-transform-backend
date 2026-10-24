"""add project_start and project_end to portfolio

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "portfolio",
        sa.Column(
            "project_start",
            sa.Date(),
            nullable=False,
            server_default=sa.func.current_date(),
        ),
    )
    op.add_column("portfolio", sa.Column("project_end", sa.Date(), nullable=True))
    op.alter_column("portfolio", "project_start", server_default=None)


def downgrade() -> None:
    op.drop_column("portfolio", "project_end")
    op.drop_column("portfolio", "project_start")
