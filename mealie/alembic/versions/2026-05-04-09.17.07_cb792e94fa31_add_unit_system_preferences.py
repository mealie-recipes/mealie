"""add unit system preferences

Revision ID: cb792e94fa31
Revises: 4395a04f7784
Create Date: 2026-05-04 09:17:07.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "cb792e94fa31"
down_revision: str | None = "4395a04f7784"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.add_column(sa.Column("default_unit_system", sa.String(), nullable=False, server_default="original"))

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("preferred_unit_system", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("preferred_unit_system")

    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.drop_column("default_unit_system")
