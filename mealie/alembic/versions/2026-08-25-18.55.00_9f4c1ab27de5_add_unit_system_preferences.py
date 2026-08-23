"""add unit system preferences

Revision ID: 9f4c1ab27de5
Revises: 69e942bab3aa
Create Date: 2026-08-25 18:55:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9f4c1ab27de5"
down_revision: str | None = "69e942bab3aa"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.add_column(sa.Column("default_unit_system", sa.String(), nullable=False, server_default="original"))
        batch_op.add_column(sa.Column("default_temperature_unit", sa.String(), nullable=False, server_default="system"))

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("preferred_unit_system", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("preferred_temperature_unit", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("preferred_temperature_unit")
        batch_op.drop_column("preferred_unit_system")

    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.drop_column("default_temperature_unit")
        batch_op.drop_column("default_unit_system")
