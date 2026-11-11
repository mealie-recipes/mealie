"""add parent_id to ingredient_foods

Revision ID: a05030850bb9
Revises: 5c1e7d2a9b3f
Create Date: 2026-11-11 12:46:14.071327

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "a05030850bb9"
down_revision: str | None = "f3a1ae61d772"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.add_column(sa.Column("parent_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(batch_op.f("ix_ingredient_foods_parent_id"), ["parent_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_ingredient_foods_parent_id",
            "ingredient_foods",
            ["parent_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ingredient_foods_parent_id"))
        batch_op.drop_column("parent_id")
