"""add reverse proxy auth method

Revision ID: f3a8b6c1d2e4
Revises: 69e942bab3aa
Create Date: 2026-09-01 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f3a8b6c1d2e4"
down_revision = "69e942bab3aa"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    if is_postgres():
        op.execute("ALTER TYPE authmethod ADD VALUE IF NOT EXISTS 'REVERSE_PROXY'")


def downgrade():
    pass
