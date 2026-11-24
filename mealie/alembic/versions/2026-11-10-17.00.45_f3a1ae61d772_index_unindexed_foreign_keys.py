"""index unindexed foreign keys

Revision ID: f3a1ae61d772
Revises: 5c1e7d2a9b3f
Create Date: 2026-11-10 17:00:45.424100

Neither SQLite nor Postgres indexes a foreign key on its own, and these composite primary keys lead
with id. Loading a recipe's ingredients, a food's or unit's aliases, or a shopping list's recipe
references scanned the whole child table for every batch.

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f3a1ae61d772"
down_revision: str | None = "5c1e7d2a9b3f"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

INDEXES = [
    ("ix_recipes_ingredients_recipe_id", "recipes_ingredients", "recipe_id"),
    ("ix_ingredient_foods_aliases_food_id", "ingredient_foods_aliases", "food_id"),
    ("ix_ingredient_units_aliases_unit_id", "ingredient_units_aliases", "unit_id"),
    (
        "ix_shopping_list_item_recipe_reference_shopping_list_item_id",
        "shopping_list_item_recipe_reference",
        "shopping_list_item_id",
    ),
    ("ix_shopping_list_recipe_reference_shopping_list_id", "shopping_list_recipe_reference", "shopping_list_id"),
]


def upgrade():
    for name, table, column in INDEXES:
        op.create_index(name, table, [column], unique=False)


def downgrade():
    for name, table, _ in INDEXES:
        op.drop_index(name, table_name=table)
