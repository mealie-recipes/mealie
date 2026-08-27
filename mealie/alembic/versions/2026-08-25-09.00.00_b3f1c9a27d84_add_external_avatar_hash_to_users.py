"""add external avatar hash to users

Revision ID: b3f1c9a27d84
Revises: 69e942bab3aa
Create Date: 2026-08-25 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b3f1c9a27d84"
down_revision: str | None = "69e942bab3aa"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("external_avatar_hash", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("external_avatar_hash")
