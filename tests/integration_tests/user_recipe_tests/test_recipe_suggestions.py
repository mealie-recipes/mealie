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
                foods=[create_food(user) for _ in range(random_int(3, 5))],
                tools=[create_tool(user) for _ in range(random_int(3, 5))],
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


def test_food_suggestion_filter_with_max(api_client: TestClient, unique_user: TestUser):
    food_1, food_2, food_3 = (create_food(unique_user) for _ in range(3))
    recipe_1 = create_recipe(unique_user, foods=[food_1])
    recipe_2 = create_recipe(unique_user, foods=[food_2])
    recipe_1_and_2 = create_recipe(unique_user, foods=[food_1, food_2])
    recipe_3 = create_recipe(unique_user, foods=[food_3])
    recipe_1_and_2_and_3 = create_recipe(unique_user, foods=[food_1, food_2, food_3])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 1, "foods": [str(food_1.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()
        data = response.json()
        fetched_recipe_ids = {item["recipe"]["id"] for item in data["items"]}
        assert set(fetched_recipe_ids) == {str(recipe_1.id), str(recipe_2.id), str(recipe_1_and_2.id), str(recipe_3.id)}
        for item in data["items"]:
            if item["recipe"]["id"] == str(recipe_1.id):
                assert item["missingFoods"] == []
            elif item["recipe"]["id"] == str(recipe_2.id) or item["recipe"]["id"] == str(recipe_1_and_2.id):
                assert item["missingFoods"] == [str(food_2.id)]
            else:
                assert item["missingFoods"] == [str(food_3.id)]

    finally:
        for recipe in [recipe_1, recipe_2, recipe_1_and_2, recipe_3, recipe_1_and_2_and_3]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_tool_suggestion_filter_with_max(api_client: TestClient, unique_user: TestUser):
    tool_1, tool_2, tool_3 = (create_tool(unique_user) for _ in range(3))
    recipe_1 = create_recipe(unique_user, tools=[tool_1])
    recipe_2 = create_recipe(unique_user, tools=[tool_2])
    recipe_1_and_2 = create_recipe(unique_user, tools=[tool_1, tool_2])
    recipe_3 = create_recipe(unique_user, tools=[tool_3])
    recipe_1_and_2_and_3 = create_recipe(unique_user, tools=[tool_1, tool_2, tool_3])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingTools": 1, "tools": [str(tool_1.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        fetched_recipe_ids = {item["recipe"]["id"] for item in data["items"]}
        assert set(fetched_recipe_ids) == {str(recipe_1.id), str(recipe_2.id), str(recipe_1_and_2.id), str(recipe_3.id)}
        for item in data["items"]:
            if item["recipe"]["id"] == str(recipe_1.id):
                assert item["missingTools"] == []
            elif item["recipe"]["id"] == str(recipe_2.id) or item["recipe"]["id"] == str(recipe_1_and_2.id):
                assert item["missingTools"] == [str(tool_2.id)]
            else:
                assert item["missingTools"] == [str(tool_3.id)]

    finally:
        for recipe in [recipe_1, recipe_2, recipe_1_and_2, recipe_3, recipe_1_and_2_and_3]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_ignore_empty_food_filter(api_client: TestClient, unique_user: TestUser):
    known_tool = create_tool(unique_user)
    recipe = create_recipe(
        unique_user, foods=[create_food(unique_user) for _ in range(random_int(3, 5))], tools=[known_tool]
    )

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "tools": [str(known_tool.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["recipe"]["id"] == str(recipe.id)
        assert item["missingFoods"] == []
        assert item["missingTools"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_ignore_empty_tool_filter(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    recipe = create_recipe(
        unique_user, foods=[known_food], tools=[create_tool(unique_user) for _ in range(random_int(3, 5))]
    )

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "foods": [str(known_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["recipe"]["id"] == str(recipe.id)
        assert item["missingFoods"] == []
        assert item["missingTools"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_include_foods_on_hand(api_client: TestClient, unique_user: TestUser):
    on_hand_food = create_food(unique_user, on_hand=True)
    off_hand_food = create_food(unique_user, on_hand=False)
    recipe = create_recipe(unique_user, foods=[on_hand_food, off_hand_food])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "foods": [str(off_hand_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["recipe"]["id"] == str(recipe.id)
        assert item["missingFoods"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_include_tools_on_hand(api_client: TestClient, unique_user: TestUser):
    on_hand_tool = create_tool(unique_user, on_hand=True)
    off_hand_tool = create_tool(unique_user, on_hand=False)
    recipe = create_recipe(unique_user, tools=[on_hand_tool, off_hand_tool])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "tools": [str(off_hand_tool.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["recipe"]["id"] == str(recipe.id)
        assert item["missingTools"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_include_recipes_with_no_foods(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    recipe_with_foods = create_recipe(unique_user, foods=[known_food])
    recipe_without_foods = create_recipe(unique_user, foods=[])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "foods": [str(known_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert {item["recipe"]["id"] for item in data["items"]} == {
            str(recipe_with_foods.id),
            str(recipe_without_foods.id),
        }
        for item in data["items"]:
            assert item["missingFoods"] == []

    finally:
        for recipe in [recipe_with_foods, recipe_without_foods]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_include_recipes_with_no_tools(api_client: TestClient, unique_user: TestUser):
    known_tool = create_tool(unique_user)
    recipe_with_tools = create_recipe(unique_user, tools=[known_tool])
    recipe_without_tools = create_recipe(unique_user, tools=[])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "tools": [str(known_tool.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert {item["recipe"]["id"] for item in data["items"]} == {
            str(recipe_with_tools.id),
            str(recipe_without_tools.id),
        }
        for item in data["items"]:
            assert item["missingTools"] == []

    finally:
        for recipe in [recipe_with_tools, recipe_without_tools]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_ignore_recipes_with_ingredient_amounts_disabled_with_foods(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    recipe_with_amounts = create_recipe(unique_user, foods=[known_food])
    recipe_without_amounts = create_recipe(unique_user, foods=[known_food], disable_amount=True)

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "foods": [str(known_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert {item["recipe"]["id"] for item in data["items"]} == {str(recipe_with_amounts.id)}
        for item in data["items"]:
            assert item["missingFoods"] == []

    finally:
        for recipe in [recipe_with_amounts, recipe_without_amounts]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_include_recipes_with_ingredient_amounts_disabled_without_foods(api_client: TestClient, unique_user: TestUser):
    known_tool = create_tool(unique_user)
    recipe_with_amounts = create_recipe(unique_user, tools=[known_tool])
    recipe_without_amounts = create_recipe(unique_user, tools=[known_tool], disable_amount=True)

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "maxMissingTools": 0, "tools": [str(known_tool.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert {item["recipe"]["id"] for item in data["items"]} == {
            str(recipe_with_amounts.id),
            str(recipe_without_amounts.id),
        }
        for item in data["items"]:
            assert item["missingFoods"] == []

    finally:
        for recipe in [recipe_with_amounts, recipe_without_amounts]:
            unique_user.repos.recipes.delete(recipe.slug)


# test ordering
# sort by missing tools asc
# sort by missing foods asc
# sort by user sort

# test food pref ordering (prefer user foods match qty)

# test limit

# test query filter

# test cross-household
