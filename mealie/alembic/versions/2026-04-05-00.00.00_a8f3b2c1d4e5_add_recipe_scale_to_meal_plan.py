"""add recipe_scale to group_meal_plans

Revision ID: a8f3b2c1d4e5
Revises: 4395a04f7784
Create Date: 2026-04-05 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f3b2c1d4e5"
down_revision: str | None = "4395a04f7784"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("group_meal_plans", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "recipe_scale",
                sa.Float(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )


def downgrade():
    with op.batch_alter_table("group_meal_plans", schema=None) as batch_op:
        batch_op.drop_column("recipe_scale")
