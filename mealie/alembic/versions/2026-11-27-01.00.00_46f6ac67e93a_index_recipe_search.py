"""Add transactional recipe search indexes.

Revision ID: 46f6ac67e93a
Revises: a136609cde0f
"""

from alembic import op

from mealie.search.index_v1 import install, uninstall

revision = "46f6ac67e93a"
down_revision = "a136609cde0f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    install(op.get_bind())


def downgrade() -> None:
    uninstall(op.get_bind())
