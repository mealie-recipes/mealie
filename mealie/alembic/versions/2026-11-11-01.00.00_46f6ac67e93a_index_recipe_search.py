"""Add transactional recipe search indexes.

Revision ID: 46f6ac67e93a
Revises: b7e6c9a2d401
"""

from alembic import op

from mealie.search.index_v1 import install, uninstall

revision = "46f6ac67e93a"
down_revision = "b7e6c9a2d401"
branch_labels = None
depends_on = None


def upgrade() -> None:
    install(op.get_bind())


def downgrade() -> None:
    uninstall(op.get_bind())
