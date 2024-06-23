"""add normalized search properties

Revision ID: 5ab195a474eb
Revises: 16160bf731a0
Create Date: 2023-02-14 20:45:41.102571

"""

import sqlalchemy as sa
from sqlalchemy import orm, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from text_unidecode import unidecode

from alembic import op
from mealie.db.models._model_utils import GUID

# revision identifiers, used by Alembic.
revision = "5ab195a474eb"
down_revision = "16160bf731a0"
branch_labels = None
depends_on = None


class SqlAlchemyBase(DeclarativeBase):
    pass


# Intermediate table definitions
class RecipeModel(SqlAlchemyBase):
    __tablename__ = "recipes"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.String)
    name_normalized: Mapped[str] = mapped_column(sa.String, nullable=False, index=True)
    description_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    note: Mapped[str | None] = mapped_column(sa.String)
    original_text: Mapped[str | None] = mapped_column(sa.String)
    note_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)
    original_text_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)


def do_data_migration():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    recipes = session.execute(select(RecipeModel)).scalars().all()
    for recipe in recipes:
        if recipe.name is not None:
            session.execute(
                sa.text(
                    f"UPDATE {RecipeModel.__tablename__} SET name_normalized=:name_normalized WHERE id=:id"
                ).bindparams(name_normalized=unidecode(recipe.name).lower().strip(), id=recipe.id)
            )

        if recipe.description is not None:
            session.execute(
                sa.text(
                    f"UPDATE {RecipeModel.__tablename__} SET description_normalized=:description_normalized WHERE id=:id"
                ).bindparams(description_normalized=unidecode(recipe.description).lower().strip(), id=recipe.id)
            )

    ingredients = session.execute(select(RecipeIngredient)).scalars().all()
    for ingredient in ingredients:
        if ingredient.note is not None:
            session.execute(
                sa.text(
                    f"UPDATE {RecipeIngredient.__tablename__} SET note_normalized=:note_normalized WHERE id=:id"
                ).bindparams(note_normalized=unidecode(ingredient.note).lower().strip(), id=ingredient.id)
            )

        if ingredient.original_text is not None:
            session.execute(
                sa.text(
                    f"UPDATE {RecipeIngredient.__tablename__} SET original_text_normalized=:original_text_normalized WHERE id=:id"
                ).bindparams(
                    original_text_normalized=unidecode(ingredient.original_text).lower().strip(), id=ingredient.id
                )
            )
    session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # Set column default first, since we do not have values here yet
    op.add_column("recipes", sa.Column("name_normalized", sa.String(), nullable=False, server_default=""))
    op.add_column("recipes", sa.Column("description_normalized", sa.String(), nullable=True))
    op.drop_index("ix_recipes_description", table_name="recipes")
    op.drop_index("ix_recipes_name", table_name="recipes")
    op.create_index(op.f("ix_recipes_description_normalized"), "recipes", ["description_normalized"], unique=False)
    op.create_index(op.f("ix_recipes_name_normalized"), "recipes", ["name_normalized"], unique=False)
    op.add_column("recipes_ingredients", sa.Column("note_normalized", sa.String(), nullable=True))
    op.add_column("recipes_ingredients", sa.Column("original_text_normalized", sa.String(), nullable=True))
    op.drop_index("ix_recipes_ingredients_note", table_name="recipes_ingredients")
    op.drop_index("ix_recipes_ingredients_original_text", table_name="recipes_ingredients")
    op.create_index(
        op.f("ix_recipes_ingredients_note_normalized"), "recipes_ingredients", ["note_normalized"], unique=False
    )
    op.create_index(
        op.f("ix_recipes_ingredients_original_text_normalized"),
        "recipes_ingredients",
        ["original_text_normalized"],
        unique=False,
    )
    do_data_migration()
    # Remove server default now that column should be filled for all rows
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.alter_column("name_normalized", existing_type=sa.String(), server_default=None)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_recipes_ingredients_original_text_normalized"), table_name="recipes_ingredients")
    op.drop_index(op.f("ix_recipes_ingredients_note_normalized"), table_name="recipes_ingredients")
    op.create_index("ix_recipes_ingredients_original_text", "recipes_ingredients", ["original_text"], unique=False)
    op.create_index("ix_recipes_ingredients_note", "recipes_ingredients", ["note"], unique=False)
    op.drop_column("recipes_ingredients", "original_text_normalized")
    op.drop_column("recipes_ingredients", "note_normalized")
    op.drop_index(op.f("ix_recipes_name_normalized"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_description_normalized"), table_name="recipes")
    op.create_index("ix_recipes_name", "recipes", ["name"], unique=False)
    op.create_index("ix_recipes_description", "recipes", ["description"], unique=False)
    op.drop_column("recipes", "description_normalized")
    op.drop_column("recipes", "name_normalized")
    # ### end Alembic commands ###
