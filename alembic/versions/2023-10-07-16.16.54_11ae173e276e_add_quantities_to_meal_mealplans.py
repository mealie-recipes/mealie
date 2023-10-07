"""add quantities to meal mealplans

Revision ID: 11ae173e276e
Revises: dded3119c1fe
Create Date: 2023-10-07 16:16:54.486076

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "11ae173e276e"
down_revision = "dded3119c1fe"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "group_meal_plans",
        sa.Column("quantity", sa.Float, nullable=False, server_default="1"),
    )
    pass


def downgrade():
    op.drop_column("group_meal_plans", "quantity")
    pass
