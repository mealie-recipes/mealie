"""add no_password_login column

Revision ID: 99bca5a25f78
Revises: 1923519381ad
Create Date: 2022-12-11 22:01:21.514971

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "99bca5a25f78"
down_revision = "1923519381ad"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("no_password_login", sa.Boolean(), nullable=False, server_default="FALSE"))


def downgrade():
    op.drop_column("users", "no_password_login")
