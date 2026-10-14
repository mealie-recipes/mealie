"""add recipe cooking method variants

Revision ID: 8d67c3ab1f42
Revises: 27621d27c7e1
Create Date: 2026-09-27 12:00:00.000000

Cooking-method variants are stored as complete recipes linked by variant_group_id. The canonical
recipe uses its own id as the implicit group id, so existing rows require no backfill.
"""

import sqlalchemy as sa

from alembic import op

import mealie.db.migration_types

revision = "8d67c3ab1f42"
down_revision: str | None = "27621d27c7e1"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cooking_method", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("variant_group_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index("ix_recipes_cooking_method", ["cooking_method"], unique=False)
        batch_op.create_index("ix_recipes_variant_group_id", ["variant_group_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.drop_index("ix_recipes_variant_group_id")
        batch_op.drop_index("ix_recipes_cooking_method")
        batch_op.drop_column("variant_group_id")
        batch_op.drop_column("cooking_method")
