"""
Responses that nest foods, units or recipe summaries must load them with the page, not with one
query per nested row. These guard against a parent schema's loader options falling out of step with
the nested schema's own.
"""

from collections.abc import Callable
from datetime import UTC, datetime

import sqlalchemy as sa

from mealie.schema.household.group_shopping_list import ShoppingListSave
from mealie.schema.meal_plan.new_meal import PlanEntrySave
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFoodAliasCreate,
    IngredientFoodSave,
    IngredientUnitAliasCreate,
    IngredientUnitSave,
)
from mealie.schema.recipe.recipe_organizers import ToolSave
from mealie.schema.response.pagination import PaginationQuery
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def count_statements(user: TestUser, load: Callable[[], object]) -> int:
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    session = user.repos.session
    session.expire_all()
    engine = session.get_bind()
    sa.event.listen(engine, "before_cursor_execute", record)
    try:
        load()
    finally:
        sa.event.remove(engine, "before_cursor_execute", record)
    return len(statements)


def test_shopping_list_query_count_does_not_grow_with_items(unique_user: TestUser):
    repos = unique_user.repos
    shopping_list = repos.group_shopping_lists.create(
        ShoppingListSave(name=random_string(), group_id=unique_user.group_id, user_id=unique_user.user_id)
    )

    def add_items(n: int):
        for _ in range(n):
            food = repos.ingredient_foods.create(
                IngredientFoodSave(
                    name=random_string(),
                    group_id=unique_user.group_id,
                    aliases=[IngredientFoodAliasCreate(name=random_string())],
                )
            )
            unit = repos.ingredient_units.create(
                IngredientUnitSave(
                    name=random_string(),
                    group_id=unique_user.group_id,
                    aliases=[IngredientUnitAliasCreate(name=random_string())],
                )
            )
            repos.group_shopping_list_item.create(
                {"shopping_list_id": shopping_list.id, "note": random_string(), "food_id": food.id, "unit_id": unit.id}
            )

    def load_list():
        loaded = repos.group_shopping_lists.get_one(shopping_list.id)
        assert loaded
        assert all(item.food and item.food.aliases for item in loaded.list_items)

    def load_items():
        page = repos.group_shopping_list_item.page_all(PaginationQuery(page=1, per_page=-1))
        assert all(item.unit and item.unit.aliases for item in page.items)

    add_items(2)
    few_list, few_items = count_statements(unique_user, load_list), count_statements(unique_user, load_items)
    add_items(6)
    assert count_statements(unique_user, load_list) == few_list
    assert count_statements(unique_user, load_items) == few_items


def test_mealplan_query_count_does_not_grow_with_recipes(unique_user: TestUser):
    repos = unique_user.repos

    def add_plans(n: int):
        for _ in range(n):
            tool = repos.tools.create(ToolSave(name=random_string(), group_id=unique_user.group_id))
            recipe = repos.recipes.create(
                RecipeDraft(
                    user_id=unique_user.user_id,
                    group_id=unique_user.group_id,
                    name=random_string(),
                    tools=[tool.model_dump()],
                )
            )
            repos.meals.create(
                PlanEntrySave(
                    date=datetime.now(UTC).date(),
                    recipe_id=recipe.id,
                    group_id=unique_user.group_id,
                    user_id=unique_user.user_id,
                )
            )

    def load_plans():
        page = repos.meals.page_all(PaginationQuery(page=1, per_page=-1))
        assert all(plan.recipe and plan.recipe.tools for plan in page.items)

    add_plans(2)
    few = count_statements(unique_user, load_plans)
    add_plans(6)
    assert count_statements(unique_user, load_plans) == few
