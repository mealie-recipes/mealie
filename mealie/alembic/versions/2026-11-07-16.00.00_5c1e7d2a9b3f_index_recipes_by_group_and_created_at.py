"""index recipes by group and created_at

Revision ID: 5c1e7d2a9b3f
Revises: 127804c19431
Create Date: 2026-11-07 16:00:00.000000

The recipe list sorts by created_at within a group by default. With only the single-column indexes,
the database reads and sorts every recipe in the group to return one page.

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "5c1e7d2a9b3f"
down_revision: str | None = "127804c19431"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_index("ix_recipes_group_id_created_at", "recipes", ["group_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_recipes_group_id_created_at", table_name="recipes")
