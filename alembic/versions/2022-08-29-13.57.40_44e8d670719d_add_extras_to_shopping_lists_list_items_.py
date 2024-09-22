"""add extras to shopping lists, list items, and ingredient foods

Revision ID: 44e8d670719d
Revises: 089bfa50d0ed
Create Date: 2022-08-29 13:57:40.452245

"""

import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "44e8d670719d"
down_revision = "089bfa50d0ed"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "shopping_list_extras",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("shopping_list_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["shopping_list_id"],
            ["shopping_lists.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ingredient_food_extras",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("ingredient_food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ingredient_food_id"],
            ["ingredient_foods.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shopping_list_item_extras",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("shopping_list_item_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["shopping_list_item_id"],
            ["shopping_list_items.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("shopping_list_item_extras")
    op.drop_table("ingredient_food_extras")
    op.drop_table("shopping_list_extras")
    # ### end Alembic commands ###
