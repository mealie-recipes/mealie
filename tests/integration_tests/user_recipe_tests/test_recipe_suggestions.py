from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import IngredientFood, RecipeIngredient, SaveIngredientFood
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.recipe.recipe_tool import RecipeToolOut, RecipeToolSave
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def create_food(user: TestUser, on_hand: bool = False):
    return user.repos.ingredient_foods.create(
        SaveIngredientFood(id=uuid4(), name=random_string(), group_id=user.group_id, on_hand=on_hand)
    )


def create_tool(user: TestUser, on_hand: bool = False):
    return user.repos.tools.create(
        RecipeToolSave(id=uuid4(), name=random_string(), group_id=user.group_id, on_hand=on_hand)
    )


def create_recipe(
    user: TestUser,
    *,
    foods: list[IngredientFood] | None = None,
    tools: list[RecipeToolOut] | None = None,
    disable_amount: bool = False,
):
    if foods:
        ingredients = [RecipeIngredient(food_id=food.id, food=food) for food in foods]
    else:
        ingredients = []

    recipe = user.repos.recipes.create(
        Recipe(
            user_id=user.user_id,
            group_id=user.group_id,
            name=random_string(),
            recipe_ingredient=ingredients,
            tools=tools or [],
            settings=RecipeSettings(disable_amount=disable_amount),
        )
    )

    return recipe


@pytest.fixture(autouse=True)
def base_recipes(unique_user: TestUser, h2_user: TestUser):
    for user in [unique_user, h2_user]:
        for _ in range(10):
            create_recipe(
                user,
                foods=[create_food(user) for _ in range(random_int(1, 5))],
                tools=[create_tool(user) for _ in range(random_int(1, 5))],
            )


@pytest.mark.parametrize("filter_foods", [True, False])
@pytest.mark.parametrize("filter_tools", [True, False])
def test_suggestion_filter(api_client: TestClient, unique_user: TestUser, filter_foods: bool, filter_tools: bool):
    create_params: dict = {}
    api_params: dict = {"maxMissingFoods": 0, "maxMissingTools": 0, "limit": 10}
    if filter_foods:
        known_food = create_food(unique_user)
        create_params["foods"] = [known_food]
        api_params["foods"] = [str(known_food.id)]
    if filter_tools:
        known_tool = create_tool(unique_user)
        create_params["tools"] = [known_tool]
        api_params["tools"] = [str(known_tool.id)]

    recipes = [create_recipe(unique_user, **create_params) for _ in range(3)]
    try:
        expected_recipe_ids = {str(recipe.id) for recipe in recipes if recipe.id}
        response = api_client.get(api_routes.recipes_suggestions, params=api_params, headers=unique_user.token)
        response.raise_for_status()
        data = response.json()

        if not filter_foods and not filter_tools:
            assert len(data["items"]) == 10
        else:
            assert len(data["items"]) == 3
            for item in data["items"]:
                assert item["recipe"]["id"] in expected_recipe_ids
                assert item["missingFoods"] == []
                assert item["missingTools"] == []
    finally:
        for recipe in recipes:
            unique_user.repos.recipes.delete(recipe.slug)


# test filter each (max = 1)
# 0 or 1 missing foods/tools
# response matches

# test filter ignores foods/tools filters if none are provided

# test filter each include on hand

# test filter includes recipes with no tools
# test filter includes recipes with no foods
# test filter excludes recipes with ingredient amounts disabled when filtering by foods

# test ordering
# sort by missing tools asc
# sort by missing foods asc
# sort by user sort

# test food pref ordering (prefer user foods match qty)

# test limit

# test query filter

# test cross-household
