"""add login_attemps and locked_at field to user table

Revision ID: 188374910655
Revises: f30cf048c228
Create Date: 2022-08-12 19:05:59.776361

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "188374910655"
down_revision = "f30cf048c228"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.add_column("users", sa.Column("login_attemps", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("locked_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("users", "locked_at")
    op.drop_column("users", "login_attemps")
