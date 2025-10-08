"""Add custom_nutrition JSON column to recipe_nutrition

Revision ID: add_custom_nutrition_column
Revises: add_nutrition_units
Create Date: 2025-09-28
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_custom_nutrition_column"
down_revision = "add_nutrition_units"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add a JSON column to hold arbitrary custom nutrition values
    op.add_column(
        "recipe_nutrition",
        sa.Column(
            "custom_nutrition",
            sa.JSON(),
            nullable=True,
            server_default=sa.text("'{}'"),  # default to empty JSON object
        ),
    )


def downgrade() -> None:
    # Drop the custom column if we roll back
    op.drop_column("recipe_nutrition", "custom_nutrition")
