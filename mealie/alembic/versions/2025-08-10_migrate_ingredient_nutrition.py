"""Add ingredient_id to nutrition and migrate data

Revision ID: 2025-08-10_migrate_ingredient_nutrition
Revises: <previous_revision_id>
Create Date: 2025-08-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Alembic migration script
# revision identifiers, used by Alembic.
revision = "2025-08-10_migrate_ingredient_nutrition"
down_revision = "<previous_revision_id>"
branch_labels = None
depends_on = None


def upgrade():
    # Add ingredient_id column to nutrition table (as string to hold GUID/UUID)
    op.add_column(
        "recipe_nutrition",
        sa.Column("ingredient_id", sa.String(length=36), nullable=True),
    )
    op.create_index("ix_recipe_nutrition_ingredient_id", "recipe_nutrition", ["ingredient_id"])

    bind = op.get_bind()
    session = Session(bind=bind)

    # Fetch ingredients with nutrition data to migrate
    ingredients = session.execute(
        sa.text(
            """
            SELECT id, calories, fat_content, carbohydrate_content
            FROM ingredients
            WHERE calories IS NOT NULL OR fat_content IS NOT NULL OR carbohydrate_content IS NOT NULL
            """
        )
    ).fetchall()

    # Batch insert nutrition linked to ingredient_id
    nutrition_rows = []
    for ingredient in ingredients:
        # Check if nutrition already exists for ingredient_id to avoid duplicates
        existing = session.execute(
            sa.text(
                "SELECT 1 FROM recipe_nutrition WHERE ingredient_id = :ingredient_id LIMIT 1"
            ),
            {"ingredient_id": ingredient.id},
        ).fetchone()

        if existing:
            continue  # Skip if already exists

        nutrition_rows.append(
            {
                "ingredient_id": ingredient.id,
                "calories": ingredient.calories,
                "fat_content": ingredient.fat_content,
                "carbohydrate_content": ingredient.carbohydrate_content,
            }
        )

    if nutrition_rows:
        session.execute(
            sa.text(
                """
                INSERT INTO recipe_nutrition (ingredient_id, calories, fat_content, carbohydrate_content)
                VALUES (:ingredient_id, :calories, :fat_content, :carbohydrate_content)
                """
            ),
            nutrition_rows,
        )

    session.commit()


def downgrade():
    # Remove ingredient_id column and index
    op.drop_index("ix_recipe_nutrition_ingredient_id", table_name="recipe_nutrition")
    op.drop_column("recipe_nutrition", "ingredient_id")
