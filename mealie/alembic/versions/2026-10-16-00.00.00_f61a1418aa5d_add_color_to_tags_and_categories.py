"""add color to tags and categories

Revision ID: f61a1418aa5d
Revises: f3a8b6c1d2e4
Create Date: 2026-10-16 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f61a1418aa5d"
down_revision = "f3a8b6c1d2e4"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.add_column(sa.Column("color", sa.String(10), nullable=False, server_default=""))

    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.add_column(sa.Column("color", sa.String(10), nullable=False, server_default=""))


def downgrade():
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.drop_column("color")

    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.drop_column("color")
