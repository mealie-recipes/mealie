"""add OIDC auth method

Revision ID: 09aba125b57a
Revises: 2298bb460ffd
Create Date: 2024-03-10 05:08:32.397027

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "09aba125b57a"
down_revision = "2298bb460ffd"
branch_labels = None
depends_on = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    if is_postgres():
        op.execute("ALTER TYPE authmethod ADD VALUE 'OIDC'")


def downgrade():
    pass
