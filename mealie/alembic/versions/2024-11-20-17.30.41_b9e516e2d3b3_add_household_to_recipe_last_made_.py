"""add household to recipe last made, household to foods, and household to tools

Revision ID: b9e516e2d3b3
Revises: b1020f328e98
Create Date: 2024-11-20 17:30:41.152332

"""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import DeclarativeBase

import mealie.db.migration_types
from alembic import op
from mealie.core.root_logger import get_logger
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.db.models._model_utils.guid import GUID

# revision identifiers, used by Alembic.
revision = "b9e516e2d3b3"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

logger = get_logger()


class SqlAlchemyBase(DeclarativeBase):
    pass


# Intermediate table definitions
class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)


class Household(SqlAlchemyBase):
    __tablename__ = "households"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)


class RecipeModel(SqlAlchemyBase):
    __tablename__ = "recipes"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    last_made: orm.Mapped[datetime | None] = orm.mapped_column(NaiveDateTime)


class HouseholdToRecipe(SqlAlchemyBase):
    __tablename__ = "households_to_recipes"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    household_id = sa.Column(GUID, sa.ForeignKey("households.id"), index=True, primary_key=True)
    recipe_id = sa.Column(GUID, sa.ForeignKey("recipes.id"), index=True, primary_key=True)
    last_made: orm.Mapped[datetime | None] = orm.mapped_column(NaiveDateTime)


class IngredientFoodModel(SqlAlchemyBase):
    __tablename__ = "ingredient_foods"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    on_hand: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)


class Tool(SqlAlchemyBase):
    __tablename__ = "tools"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    on_hand: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, default=False)


def migrate_recipe_last_made_to_household(session: orm.Session):
    for group in session.query(Group).all():
        households = session.query(Household).filter(Household.group_id == group.id).all()
        recipes = (
            session.query(RecipeModel)
            .filter(
                RecipeModel.group_id == group.id,
                RecipeModel.last_made != None,  # noqa E711
            )
            .all()
        )

        for recipe in recipes:
            for household in households:
                session.add(
                    HouseholdToRecipe(
                        household_id=household.id,
                        recipe_id=recipe.id,
                        last_made=recipe.last_made,
                    )
                )


def migrate_foods_on_hand_to_household(session: orm.Session):
    dialect = op.get_bind().dialect

    for group in session.query(Group).all():
        households = session.query(Household).filter(Household.group_id == group.id).all()
        foods = (
            session.query(IngredientFoodModel)
            .filter(
                IngredientFoodModel.group_id == group.id,
                IngredientFoodModel.on_hand == True,  # noqa E712
            )
            .all()
        )

        for food in foods:
            for household in households:
                session.execute(
                    sa.text(
                        "INSERT INTO households_to_ingredient_foods (household_id, food_id)"
                        "VALUES (:household_id, :food_id)"
                    ),
                    {
                        "household_id": GUID.convert_value_to_guid(household.id, dialect),
                        "food_id": GUID.convert_value_to_guid(food.id, dialect),
                    },
                )


def migrate_tools_on_hand_to_household(session: orm.Session):
    dialect = op.get_bind().dialect

    for group in session.query(Group).all():
        households = session.query(Household).filter(Household.group_id == group.id).all()
        tools = (
            session.query(Tool)
            .filter(
                Tool.group_id == group.id,
                Tool.on_hand == True,  # noqa E712
            )
            .all()
        )

        for tool in tools:
            for household in households:
                session.execute(
                    sa.text("INSERT INTO households_to_tools (household_id, tool_id) VALUES (:household_id, :tool_id)"),
                    {
                        "household_id": GUID.convert_value_to_guid(household.id, dialect),
                        "tool_id": GUID.convert_value_to_guid(tool.id, dialect),
                    },
                )


def migrate_to_new_models():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for migration_func in [
        migrate_recipe_last_made_to_household,
        migrate_foods_on_hand_to_household,
        migrate_tools_on_hand_to_household,
    ]:
        try:
            logger.info(f"Running new model migration ({migration_func.__name__})")
            migration_func(session)
            session.commit()
        except Exception:
            session.rollback()
            logger.error(f"Error during new model migration ({migration_func.__name__})")
            raise


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "households_to_recipes",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("last_made", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id", "household_id", "recipe_id"),
        sa.UniqueConstraint("household_id", "recipe_id", name="household_id_recipe_id_key"),
    )
    with op.batch_alter_table("households_to_recipes", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_households_to_recipes_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_households_to_recipes_household_id"), ["household_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_households_to_recipes_recipe_id"), ["recipe_id"], unique=False)

    op.create_table(
        "households_to_tools",
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("tool_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tools.id"],
        ),
        sa.UniqueConstraint("household_id", "tool_id", name="household_id_tool_id_key"),
    )
    with op.batch_alter_table("households_to_tools", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_households_to_tools_household_id"), ["household_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_households_to_tools_tool_id"), ["tool_id"], unique=False)

    op.create_table(
        "households_to_ingredient_foods",
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["food_id"],
            ["ingredient_foods.id"],
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.UniqueConstraint("household_id", "food_id", name="household_id_food_id_key"),
    )
    with op.batch_alter_table("households_to_ingredient_foods", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_households_to_ingredient_foods_food_id"), ["food_id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_households_to_ingredient_foods_household_id"), ["household_id"], unique=False
        )

    # ### end Alembic commands ###

    migrate_to_new_models()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("households_to_ingredient_foods", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_households_to_ingredient_foods_household_id"))
        batch_op.drop_index(batch_op.f("ix_households_to_ingredient_foods_food_id"))

    op.drop_table("households_to_ingredient_foods")
    with op.batch_alter_table("households_to_tools", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_households_to_tools_tool_id"))
        batch_op.drop_index(batch_op.f("ix_households_to_tools_household_id"))

    op.drop_table("households_to_tools")
    with op.batch_alter_table("households_to_recipes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_households_to_recipes_recipe_id"))
        batch_op.drop_index(batch_op.f("ix_households_to_recipes_household_id"))
        batch_op.drop_index(batch_op.f("ix_households_to_recipes_created_at"))

    op.drop_table("households_to_recipes")
    # ### end Alembic commands ###
