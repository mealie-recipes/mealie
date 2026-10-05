"""Preserve deleted food descriptions on recipes and shopping list items."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "8e2a6621f001"
down_revision = "3527efeeec34"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("recipes_ingredients", "shopping_list_items"):
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(
                sa.Column(
                    "food_snapshot",
                    sa.JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql"),
                    nullable=True,
                )
            )


def downgrade():
    for table in ("shopping_list_items", "recipes_ingredients"):
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_column("food_snapshot")
