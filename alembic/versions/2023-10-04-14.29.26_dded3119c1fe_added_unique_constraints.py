"""added unique constraints

Revision ID: dded3119c1fe
Revises: 0341b154f79a
Create Date: 2023-10-04 14:29:26.688065

"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from pydantic import UUID4
from sqlalchemy import orm
from sqlalchemy.orm import Session, load_only

from alembic import op
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel, RecipeIngredientModel

# revision identifiers, used by Alembic.
revision = "dded3119c1fe"
down_revision = "0341b154f79a"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


# Intermediate table definitions
class SqlAlchemyBase(orm.DeclarativeBase):
    pass


class ShoppingList(SqlAlchemyBase):
    __tablename__ = "shopping_lists"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)


class ShoppingListItem(SqlAlchemyBase):
    __tablename__ = "shopping_list_items"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    food_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("ingredient_foods.id"))
    unit_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("ingredient_units.id"))
    label_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("multi_purpose_labels.id"))


@dataclass
class TableMeta:
    tablename: str
    pk_1: str
    pk_2: str

    @classmethod
    def composite_pk(self, pk_1_val: Any, pk_2_val: Any) -> str:
        return "$$".join([pk_1_val, pk_2_val])


def _is_postgres():
    return op.get_context().dialect.name == "postgresql"


def _get_duplicates(session: Session, model: orm.DeclarativeBase) -> defaultdict[str, list]:
    duplicate_map: defaultdict[str, list] = defaultdict(list)

    query = session.execute(sa.text(f"SELECT id, group_id, name FROM {model.__tablename__}"))
    for row in query.all():
        id, group_id, name = row
        key = f"{group_id}$${name}"
        duplicate_map[key].append(id)

    return duplicate_map


def _resolve_duplicate_food(
    session: Session,
    keep_food_id: UUID4,
    dupe_food_id: UUID4,
):
    for shopping_list_item in (
        session.query(ShoppingListItem)
        .options(load_only(ShoppingListItem.id, ShoppingListItem.food_id))
        .filter_by(food_id=dupe_food_id)
        .all()
    ):
        shopping_list_item.food_id = keep_food_id

    for recipe_ingredient in (
        session.query(RecipeIngredientModel)
        .options(load_only(RecipeIngredientModel.id, RecipeIngredientModel.food_id))
        .filter_by(food_id=dupe_food_id)
        .all()
    ):
        recipe_ingredient.food_id = keep_food_id

    session.commit()
    session.execute(
        sa.text(f"DELETE FROM {IngredientFoodModel.__tablename__} WHERE id=:id").bindparams(id=dupe_food_id)
    )
    session.commit()


def _resolve_duplicate_unit(
    session: Session,
    keep_unit_id: UUID4,
    dupe_unit_id: UUID4,
):
    for shopping_list_item in (
        session.query(ShoppingListItem)
        .options(load_only(ShoppingListItem.id, ShoppingListItem.unit_id))
        .filter_by(unit_id=dupe_unit_id)
        .all()
    ):
        shopping_list_item.unit_id = keep_unit_id

    for recipe_ingredient in (
        session.query(RecipeIngredientModel)
        .options(load_only(RecipeIngredientModel.id, RecipeIngredientModel.unit_id))
        .filter_by(unit_id=dupe_unit_id)
        .all()
    ):
        recipe_ingredient.unit_id = keep_unit_id

    session.commit()
    session.execute(
        sa.text(f"DELETE FROM {IngredientUnitModel.__tablename__} WHERE id=:id").bindparams(id=dupe_unit_id)
    )
    session.commit()


def _resolve_duplicate_label(
    session: Session,
    keep_label_id: UUID4,
    dupe_label_id: UUID4,
):
    for shopping_list_item in (
        session.query(ShoppingListItem)
        .options(load_only(ShoppingListItem.id, ShoppingListItem.label_id))
        .filter_by(label_id=dupe_label_id)
        .all()
    ):
        shopping_list_item.label_id = keep_label_id

    for ingredient_food in (
        session.query(IngredientFoodModel)
        .options(load_only(IngredientFoodModel.id, IngredientFoodModel.label_id))
        .filter_by(label_id=dupe_label_id)
        .all()
    ):
        ingredient_food.label_id = keep_label_id

    session.commit()
    session.execute(sa.text(f"DELETE FROM {MultiPurposeLabel.__tablename__} WHERE id=:id").bindparams(id=dupe_label_id))
    session.commit()


def _resolve_duplicate_foods_units_labels(session: Session):
    for model, resolve_func in [
        (IngredientFoodModel, _resolve_duplicate_food),
        (IngredientUnitModel, _resolve_duplicate_unit),
        (MultiPurposeLabel, _resolve_duplicate_label),
    ]:
        duplicate_map = _get_duplicates(session, model)
        for ids in duplicate_map.values():
            if len(ids) < 2:
                continue

            keep_id = ids[0]
            for dupe_id in ids[1:]:
                resolve_func(session, keep_id, dupe_id)


def _remove_duplicates_from_m2m_table(session: Session, table_meta: TableMeta):
    if _is_postgres():
        default_pk = "CTID"
    else:
        default_pk = "ROWID"

    # some of these tables are missing defined unique pks, so we have to rely on the database default pk
    query = sa.text(
        f"""
        DELETE FROM {table_meta.tablename}
        WHERE EXISTS (
            SELECT 1 FROM {table_meta.tablename} t2
            WHERE {table_meta.tablename}.{table_meta.pk_1} = t2.{table_meta.pk_1}
            AND {table_meta.tablename}.{table_meta.pk_2} = t2.{table_meta.pk_2}
            AND {table_meta.tablename}.{default_pk} > t2.{default_pk}
        )
        """
    )

    session.execute(query)
    session.commit()


def _remove_duplicates_from_m2m_tables(session: Session, table_metas: list[TableMeta]):
    for table_meta in table_metas:
        _remove_duplicates_from_m2m_table(session, table_meta)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    _resolve_duplicate_foods_units_labels(session)
    _remove_duplicates_from_m2m_tables(
        session,
        [
            TableMeta("cookbooks_to_categories", "cookbook_id", "category_id"),
            TableMeta("cookbooks_to_tags", "cookbook_id", "tag_id"),
            TableMeta("cookbooks_to_tools", "cookbook_id", "tool_id"),
            TableMeta("group_to_categories", "group_id", "category_id"),
            TableMeta("plan_rules_to_categories", "group_plan_rule_id", "category_id"),
            TableMeta("plan_rules_to_tags", "plan_rule_id", "tag_id"),
            TableMeta("recipes_to_categories", "recipe_id", "category_id"),
            TableMeta("recipes_to_tags", "recipe_id", "tag_id"),
            TableMeta("recipes_to_tools", "recipe_id", "tool_id"),
            TableMeta("users_to_favorites", "user_id", "recipe_id"),
            TableMeta("shopping_lists_multi_purpose_labels", "shopping_list_id", "label_id"),
        ],
    )

    session.commit()

    # ### commands auto generated by Alembic - please adjust! ###
    # we use batch_alter_table here because otherwise this fails on sqlite
    # M2M
    with op.batch_alter_table("cookbooks_to_categories") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_category_id_key", ["cookbook_id", "category_id"])

    with op.batch_alter_table("cookbooks_to_tags") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_tag_id_key", ["cookbook_id", "tag_id"])

    with op.batch_alter_table("cookbooks_to_tools") as batch_op:
        batch_op.create_unique_constraint("cookbook_id_tool_id_key", ["cookbook_id", "tool_id"])

    with op.batch_alter_table("group_to_categories") as batch_op:
        batch_op.create_unique_constraint("group_id_category_id_key", ["group_id", "category_id"])

    with op.batch_alter_table("plan_rules_to_categories") as batch_op:
        batch_op.create_unique_constraint("group_plan_rule_id_category_id_key", ["group_plan_rule_id", "category_id"])

    with op.batch_alter_table("plan_rules_to_tags") as batch_op:
        batch_op.create_unique_constraint("plan_rule_id_tag_id_key", ["plan_rule_id", "tag_id"])

    with op.batch_alter_table("recipes_to_categories") as batch_op:
        batch_op.create_unique_constraint("recipe_id_category_id_key", ["recipe_id", "category_id"])

    with op.batch_alter_table("recipes_to_tags") as batch_op:
        batch_op.create_unique_constraint("recipe_id_tag_id_key", ["recipe_id", "tag_id"])

    with op.batch_alter_table("recipes_to_tools") as batch_op:
        batch_op.create_unique_constraint("recipe_id_tool_id_key", ["recipe_id", "tool_id"])

    with op.batch_alter_table("users_to_favorites") as batch_op:
        batch_op.create_unique_constraint("user_id_recipe_id_key", ["user_id", "recipe_id"])

    with op.batch_alter_table("shopping_lists_multi_purpose_labels") as batch_op:
        batch_op.create_unique_constraint("shopping_list_id_label_id_key", ["shopping_list_id", "label_id"])

    # Foods/Units/Labels
    with op.batch_alter_table("ingredient_foods") as batch_op:
        batch_op.create_unique_constraint("ingredient_foods_name_group_id_key", ["name", "group_id"])

    with op.batch_alter_table("ingredient_units") as batch_op:
        batch_op.create_unique_constraint("ingredient_units_name_group_id_key", ["name", "group_id"])

    with op.batch_alter_table("multi_purpose_labels") as batch_op:
        batch_op.create_unique_constraint("multi_purpose_labels_name_group_id_key", ["name", "group_id"])

    op.create_index(
        op.f("ix_shopping_lists_multi_purpose_labels_created_at"),
        "shopping_lists_multi_purpose_labels",
        ["created_at"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # M2M
    op.drop_constraint("user_id_recipe_id_key", "users_to_favorites", type_="unique")
    op.drop_index(
        op.f("ix_shopping_lists_multi_purpose_labels_created_at"), table_name="shopping_lists_multi_purpose_labels"
    )
    op.drop_constraint("recipe_id_tool_id_key", "recipes_to_tools", type_="unique")
    op.drop_constraint("recipe_id_tag_id_key", "recipes_to_tags", type_="unique")
    op.drop_constraint("recipe_id_category_id_key", "recipes_to_categories", type_="unique")
    op.drop_constraint("plan_rule_id_tag_id_key", "plan_rules_to_tags", type_="unique")
    op.drop_constraint("group_plan_rule_id_category_id_key", "plan_rules_to_categories", type_="unique")
    op.drop_constraint("group_id_category_id_key", "group_to_categories", type_="unique")
    op.drop_constraint("cookbook_id_tool_id_key", "cookbooks_to_tools", type_="unique")
    op.drop_constraint("cookbook_id_tag_id_key", "cookbooks_to_tags", type_="unique")
    op.drop_constraint("cookbook_id_category_id_key", "cookbooks_to_categories", type_="unique")
    op.drop_constraint("shopping_list_id_label_id_key", "shopping_lists_multi_purpose_labels", type_="unique")

    # Foods/Units/Labels
    op.drop_constraint("multi_purpose_labels_name_group_id_key", "multi_purpose_labels", type_="unique")
    op.drop_constraint("ingredient_units_name_group_id_key", "ingredient_units", type_="unique")
    op.drop_constraint("ingredient_foods_name_group_id_key", "ingredient_foods", type_="unique")
    # ### end Alembic commands ###
