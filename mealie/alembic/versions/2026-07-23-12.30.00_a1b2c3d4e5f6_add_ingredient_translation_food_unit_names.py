"""add ingredient translation food/unit names

Revision ID: a1b2c3d4e5f6
Revises: 910c8c9ed8d4
Create Date: 2026-07-23 12:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "910c8c9ed8d4"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("recipe_ingredient_translations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("food_name", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("unit_name", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("recipe_ingredient_translations", schema=None) as batch_op:
        batch_op.drop_column("unit_name")
        batch_op.drop_column("food_name")
