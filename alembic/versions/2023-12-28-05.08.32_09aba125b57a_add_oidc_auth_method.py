"""add OIDC auth method

Revision ID: 09aba125b57a
Revises: ba1e4a6cfe99
Create Date: 2023-12-28 05:08:32.397027

"""

import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "09aba125b57a"
down_revision = "ba1e4a6cfe99"
branch_labels = None
depends_on = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    if is_postgres():
        op.execute("ALTER TYPE authmethod ADD VALUE 'OIDC'")


def downgrade():
    pass
