"""Track recipe migration identities within each household.

Revision ID: e4b68c9a105d
Revises: 27621d27c7e1
"""

import sqlalchemy as sa
from alembic import op
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models._model_utils.datetime import NaiveDateTime

revision = "e4b68c9a105d"
down_revision = "27621d27c7e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_migrations",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("household_id", GUID(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("recipe_id", GUID(), nullable=False),
        sa.Column("created_at", NaiveDateTime(), nullable=True),
        sa.Column("update_at", NaiveDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("household_id", "source", "fingerprint", name="uq_recipe_migration_source"),
    )
    op.create_index("ix_recipe_migrations_recipe_id", "recipe_migrations", ["recipe_id"])
    op.create_index("ix_recipe_migrations_created_at", "recipe_migrations", ["created_at"])


def downgrade() -> None:
    op.drop_table("recipe_migrations")
