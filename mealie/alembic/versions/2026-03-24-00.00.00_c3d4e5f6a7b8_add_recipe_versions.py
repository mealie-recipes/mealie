"""Add recipe_versions table

Revision ID: c3d4e5f6a7b8
Revises: a39c7f1826e3
Create Date: 2026-03-24 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from mealie.db.models._model_utils.guid import GUID

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision: str | None = "a39c7f1826e3"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_table(
        "recipe_versions",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("recipe_id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=True),
        sa.Column("group_id", GUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("snapshot", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recipe_versions_recipe_id", "recipe_versions", ["recipe_id"])
    op.create_index("ix_recipe_versions_group_id", "recipe_versions", ["group_id"])
    op.create_index("ix_recipe_versions_recipe_id_version", "recipe_versions", ["recipe_id", "version_number"])


def downgrade():
    op.drop_index("ix_recipe_versions_recipe_id_version", table_name="recipe_versions")
    op.drop_index("ix_recipe_versions_group_id", table_name="recipe_versions")
    op.drop_index("ix_recipe_versions_recipe_id", table_name="recipe_versions")
    op.drop_table("recipe_versions")
