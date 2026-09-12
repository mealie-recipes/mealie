"""add private column to recipe settings

Revision ID: 4f9a1c2e8b3d
Revises: 4b91d3a7c0e2
Create Date: 2026-09-05 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4f9a1c2e8b3d"
down_revision: str | None = "4b91d3a7c0e2"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column(
        "recipe_settings",
        sa.Column("private", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("recipe_settings", "private")
