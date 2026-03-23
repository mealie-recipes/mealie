"""Add Nextcloud Tasks preferences to household_preferences

Revision ID: b1c2d3e4f5a6
Revises: a39c7f1826e3
Create Date: 2026-03-23 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5a6"
down_revision: str | None = "a39c7f1826e3"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("nextcloud_enabled", sa.Boolean(), nullable=True, default=False, server_default=sa.sql.expression.false())
        )
        batch_op.add_column(sa.Column("nextcloud_url", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("nextcloud_username", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("nextcloud_password", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("nextcloud_task_list", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("nextcloud_verify_ssl", sa.Boolean(), nullable=True, default=True, server_default=sa.sql.expression.true())
        )


def downgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.drop_column("nextcloud_verify_ssl")
        batch_op.drop_column("nextcloud_task_list")
        batch_op.drop_column("nextcloud_password")
        batch_op.drop_column("nextcloud_username")
        batch_op.drop_column("nextcloud_url")
        batch_op.drop_column("nextcloud_enabled")
