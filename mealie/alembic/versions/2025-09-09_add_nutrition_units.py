"""Add unit columns to recipe_nutrition table

Revision ID: add_nutrition_units
Revises: e6bb583aac2d
Create Date: 2025-09-09

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_nutrition_units"
down_revision = "e6bb583aac2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("recipe_nutrition", sa.Column("calories_unit", sa.String(), nullable=True, server_default="kcal"))
    op.add_column(
        "recipe_nutrition", sa.Column("carbohydrate_content_unit", sa.String(), nullable=True, server_default="g")
    )
    op.add_column(
        "recipe_nutrition", sa.Column("cholesterol_content_unit", sa.String(), nullable=True, server_default="mg")
    )
    op.add_column("recipe_nutrition", sa.Column("fat_content_unit", sa.String(), nullable=True, server_default="g"))
    op.add_column("recipe_nutrition", sa.Column("fiber_content_unit", sa.String(), nullable=True, server_default="g"))
    op.add_column("recipe_nutrition", sa.Column("protein_content_unit", sa.String(), nullable=True, server_default="g"))
    op.add_column(
        "recipe_nutrition", sa.Column("saturated_fat_content_unit", sa.String(), nullable=True, server_default="g")
    )
    op.add_column("recipe_nutrition", sa.Column("sodium_content_unit", sa.String(), nullable=True, server_default="mg"))
    op.add_column("recipe_nutrition", sa.Column("sugar_content_unit", sa.String(), nullable=True, server_default="g"))
    op.add_column(
        "recipe_nutrition", sa.Column("trans_fat_content_unit", sa.String(), nullable=True, server_default="g")
    )
    op.add_column(
        "recipe_nutrition", sa.Column("unsaturated_fat_content_unit", sa.String(), nullable=True, server_default="g")
    )


def downgrade() -> None:
    op.drop_column("recipe_nutrition", "unsaturated_fat_content_unit")
    op.drop_column("recipe_nutrition", "trans_fat_content_unit")
    op.drop_column("recipe_nutrition", "sugar_content_unit")
    op.drop_column("recipe_nutrition", "sodium_content_unit")
    op.drop_column("recipe_nutrition", "saturated_fat_content_unit")
    op.drop_column("recipe_nutrition", "protein_content_unit")
    op.drop_column("recipe_nutrition", "fiber_content_unit")
    op.drop_column("recipe_nutrition", "fat_content_unit")
    op.drop_column("recipe_nutrition", "cholesterol_content_unit")
    op.drop_column("recipe_nutrition", "carbohydrate_content_unit")
    op.drop_column("recipe_nutrition", "calories_unit")
