"""added unique constraints

Revision ID: dded3119c1fe
Revises: 0341b154f79a
Create Date: 2023-10-04 14:29:26.688065

"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session

import mealie.db.migration_types
from alembic import op
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models.group.shopping_list import ShoppingListItem
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel, RecipeIngredientModel

# revision identifiers, used by Alembic.
revision = "dded3119c1fe"
down_revision = "0341b154f79a"
branch_labels = None
depends_on = None


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


def _get_duplicates(session: Session, model: SqlAlchemyBase) -> defaultdict[str, list[str]]:
    duplicate_map: defaultdict[str, list[str]] = defaultdict(list)
    for obj in session.query(model).all():
        key = f"{obj.group_id}$${obj.name}"
        duplicate_map[key].append(str(obj.id))

    return duplicate_map


def _resolve_duplicate_food(session: Session, keep_food: IngredientFoodModel, dupe_food: IngredientFoodModel):
    for shopping_list_item in session.query(ShoppingListItem).filter_by(food_id=dupe_food.id).all():
        shopping_list_item.food_id = keep_food.id
        shopping_list_item.food = keep_food

    session.commit()

    for recipe_ingredient in session.query(RecipeIngredientModel).filter_by(food_id=dupe_food.id).all():
        recipe_ingredient.food_id = keep_food.id
        recipe_ingredient.food = keep_food

    session.commit()

    session.delete(dupe_food)
    session.commit()


def _resolve_duplicate_unit(session: Session, keep_unit: IngredientUnitModel, dupe_unit: IngredientUnitModel):
    for shopping_list_item in session.query(ShoppingListItem).filter_by(unit_id=dupe_unit.id).all():
        shopping_list_item.unit_id = keep_unit.id
        shopping_list_item.unit = keep_unit

    session.commit()

    for recipe_ingredient in session.query(RecipeIngredientModel).filter_by(unit_id=dupe_unit.id).all():
        recipe_ingredient.unit_id = keep_unit.id
        recipe_ingredient.unit = keep_unit

    session.commit()

    session.delete(dupe_unit)
    session.commit()


def _resolve_duplicate_label(session: Session, keep_label: MultiPurposeLabel, dupe_label: MultiPurposeLabel):
    for shopping_list_item in session.query(ShoppingListItem).filter_by(label_id=dupe_label.id).all():
        shopping_list_item.label_id = keep_label.id
        shopping_list_item.label = keep_label

    session.commit()

    for ingredient_food in session.query(IngredientFoodModel).filter_by(label_id=dupe_label.id).all():
        ingredient_food.label_id = keep_label.id
        ingredient_food.label = keep_label

    session.commit()

    session.delete(dupe_label)
    session.commit()


def _resolve_duplivate_foods_units_labels():
    bind = op.get_bind()
    session = Session(bind=bind)

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
            keep_obj = session.query(model).filter_by(id=keep_id).first()
            for dupe_id in ids[1:]:
                dupe_obj = session.query(model).filter_by(id=dupe_id).first()
                resolve_func(session, keep_obj, dupe_obj)


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


def _remove_duplicates_from_m2m_tables(table_metas: list[TableMeta]):
    bind = op.get_bind()
    session = Session(bind=bind)

    for table_meta in table_metas:
        _remove_duplicates_from_m2m_table(session, table_meta)


def upgrade():
    _resolve_duplivate_foods_units_labels()
    _remove_duplicates_from_m2m_tables(
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
        ]
    )

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
