import random
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
    if on_hand:
        household = user.repos.households.get_by_slug_or_id(user.household_id)
        assert household
        households = [household.slug]
    else:
        households = []

    return user.repos.ingredient_foods.create(
        SaveIngredientFood(
            id=uuid4(), name=random_string(), group_id=user.group_id, households_with_ingredient_food=households
        )
    )


def create_tool(user: TestUser, on_hand: bool = False):
    if on_hand:
        household = user.repos.households.get_by_slug_or_id(user.household_id)
        assert household
        households = [household.slug]
    else:
        households = []

    return user.repos.tools.create(
        RecipeToolSave(
            id=uuid4(), name=random_string(), group_id=user.group_id, on_hand=on_hand, households_with_tool=households
        )
    )


def create_recipe(
    user: TestUser,
    *,
    foods: list[IngredientFood] | None = None,
    tools: list[RecipeToolOut] | None = None,
    disable_amount: bool = False,
    **kwargs,
):
    if foods:
        ingredients = [RecipeIngredient(food_id=food.id, food=food) for food in foods]
    else:
        ingredients = []

    recipe = user.repos.recipes.create(
        Recipe(
            user_id=user.user_id,
            group_id=user.group_id,
            name=kwargs.pop("name", random_string()),
            recipe_ingredient=ingredients,
            tools=tools or [],
            settings=RecipeSettings(disable_amount=disable_amount),
            **kwargs,
        )
    )

    return recipe


@pytest.fixture(autouse=True)
def base_recipes(unique_user: TestUser, h2_user: TestUser):
    for user in [unique_user, h2_user]:
        for _ in range(10):
            create_recipe(
                user,
                foods=[create_food(user) for _ in range(random_int(5, 10))],
                tools=[create_tool(user) for _ in range(random_int(5, 10))],
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
    food_1, food_2, food_3, food_4 = (create_food(unique_user) for _ in range(4))
    recipe_exact = create_recipe(unique_user, foods=[food_1])
    recipe_missing_one = create_recipe(unique_user, foods=[food_1, food_2])
    recipe_missing_two = create_recipe(unique_user, foods=[food_1, food_2, food_3])
    recipe_missing_three = create_recipe(unique_user, foods=[food_1, food_2, food_3, food_4])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 1, "includeFoodsOnHand": False, "foods": [str(food_1.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()
        data = response.json()
        fetched_recipe_ids = {item["recipe"]["id"] for item in data["items"]}
        assert set(fetched_recipe_ids) == {str(recipe_exact.id), str(recipe_missing_one.id)}
        for item in data["items"]:
            missing_food_ids = [food["id"] for food in item["missingFoods"]]
            if item["recipe"]["id"] == str(recipe_exact.id):
                assert missing_food_ids == []
            else:
                assert missing_food_ids == [str(food_2.id)]

    finally:
        for recipe in [recipe_exact, recipe_missing_one, recipe_missing_two, recipe_missing_three]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_tool_suggestion_filter_with_max(api_client: TestClient, unique_user: TestUser):
    tool_1, tool_2, tool_3, tool_4 = (create_tool(unique_user) for _ in range(4))
    recipe_exact = create_recipe(unique_user, tools=[tool_1])
    recipe_missing_one = create_recipe(unique_user, tools=[tool_1, tool_2])
    recipe_missing_two = create_recipe(unique_user, tools=[tool_1, tool_2, tool_3])
    recipe_missing_three = create_recipe(unique_user, tools=[tool_1, tool_2, tool_3, tool_4])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingTools": 1, "includeToolsOnHand": False, "tools": [str(tool_1.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        fetched_recipe_ids = {item["recipe"]["id"] for item in data["items"]}
        assert set(fetched_recipe_ids) == {str(recipe_exact.id), str(recipe_missing_one.id)}
        for item in data["items"]:
            missing_tool_ids = [tool["id"] for tool in item["missingTools"]]
            if item["recipe"]["id"] == str(recipe_exact.id):
                assert missing_tool_ids == []
            else:
                assert missing_tool_ids == [str(tool_2.id)]

    finally:
        for recipe in [recipe_exact, recipe_missing_one, recipe_missing_two, recipe_missing_three]:
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


@pytest.mark.parametrize("include_on_hand", [True, False])
def test_include_foods_on_hand(api_client: TestClient, unique_user: TestUser, include_on_hand: bool):
    on_hand_food = create_food(unique_user, on_hand=True)
    off_hand_food = create_food(unique_user, on_hand=False)
    recipe = create_recipe(unique_user, foods=[on_hand_food, off_hand_food])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={
                "maxMissingFoods": 0,
                "maxMissingTools": 0,
                "includeFoodsOnHand": include_on_hand,
                "foods": [str(off_hand_food.id)],
            },
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        if not include_on_hand:
            assert len(data["items"]) == 0
        else:
            assert len(data["items"]) == 1
            item = data["items"][0]
            assert item["recipe"]["id"] == str(recipe.id)
            assert item["missingFoods"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


@pytest.mark.parametrize("include_on_hand", [True, False])
def test_include_tools_on_hand(api_client: TestClient, unique_user: TestUser, include_on_hand: bool):
    on_hand_tool = create_tool(unique_user, on_hand=True)
    off_hand_tool = create_tool(unique_user, on_hand=False)
    recipe = create_recipe(unique_user, tools=[on_hand_tool, off_hand_tool])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={
                "maxMissingFoods": 0,
                "maxMissingTools": 0,
                "includeToolsOnHand": include_on_hand,
                "tools": [str(off_hand_tool.id)],
            },
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        if not include_on_hand:
            assert len(data["items"]) == 0
        else:
            assert len(data["items"]) == 1
            item = data["items"][0]
            assert item["recipe"]["id"] == str(recipe.id)
            assert item["missingTools"] == []

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_exclude_recipes_with_no_foods(api_client: TestClient, unique_user: TestUser):
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
        assert {item["recipe"]["id"] for item in data["items"]} == {str(recipe_with_foods.id)}
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
            params={
                "maxMissingFoods": 0,
                "maxMissingTools": 0,
                "includeFoodsOnHand": False,
                "tools": [str(known_tool.id)],
            },
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


def test_exclude_recipes_with_no_user_foods(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    food_on_hand = create_food(unique_user, on_hand=True)
    recipe_with_user_food = create_recipe(unique_user, foods=[known_food])
    recipe_with_on_hand_food = create_recipe(unique_user, foods=[food_on_hand])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 10, "includeFoodsOnHand": True, "foods": [str(known_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert {item["recipe"]["id"] for item in data["items"]} == {str(recipe_with_user_food.id)}
        assert data["items"][0]["missingFoods"] == []

    finally:
        for recipe in [recipe_with_user_food, recipe_with_on_hand_food]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_recipe_order(api_client: TestClient, unique_user: TestUser):
    user_food_1, user_food_2, other_food_1, other_food_2, other_food_3 = (create_food(unique_user) for _ in range(5))
    user_tool_1, other_tool_1, other_tool_2 = (create_tool(unique_user) for _ in range(3))
    food_on_hand = create_food(unique_user, on_hand=True)

    recipe_lambdas = [
        # No missing tools or foods
        (0, lambda: create_recipe(unique_user, tools=[user_tool_1], foods=[user_food_1])),
        # No missing tools, one missing food
        (1, lambda: create_recipe(unique_user, tools=[user_tool_1], foods=[user_food_1, other_food_1])),
        # One missing tool, no missing foods
        (2, lambda: create_recipe(unique_user, tools=[user_tool_1, other_tool_1], foods=[user_food_1])),
        # One missing tool, one missing food
        (3, lambda: create_recipe(unique_user, tools=[user_tool_1, other_tool_1], foods=[user_food_1, other_food_1])),
        # Two missing tools, two missing foods, two user foods
        (
            4,
            lambda: create_recipe(
                unique_user,
                tools=[user_tool_1, other_tool_1, other_tool_2],
                foods=[user_food_1, user_food_2, other_food_1, other_food_2],
            ),
        ),
        # Two missing tools, two missing foods, one user food
        (
            5,
            lambda: create_recipe(
                unique_user,
                tools=[user_tool_1, other_tool_1, other_tool_2],
                foods=[user_food_1, other_food_1, other_food_2],
            ),
        ),
        # Two missing tools, three missing foods, two user foods, don't include food on hand
        (
            6,
            lambda: create_recipe(
                unique_user,
                tools=[user_tool_1, other_tool_1, other_tool_2],
                foods=[user_food_1, user_food_2, other_food_1, other_food_2, other_food_3],
            ),
        ),
        # Two missing tools, three missing foods, one user food, include food on hand
        (
            7,
            lambda: create_recipe(
                unique_user,
                tools=[user_tool_1, other_tool_1, other_tool_2],
                foods=[food_on_hand, user_food_1, other_food_1, other_food_2, other_food_3],
            ),
        ),
    ]

    # create recipes in a random order
    random.shuffle(recipe_lambdas)
    recipe_tuples: list[tuple[int, Recipe]] = []
    for i, recipe_lambda in recipe_lambdas:
        recipe_tuples.append((i, recipe_lambda()))

    recipe_tuples.sort(key=lambda x: x[0])
    recipes = [recipe_tuple[1] for recipe_tuple in recipe_tuples]

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={
                "maxMissingFoods": 3,
                "maxMissingTools": 3,
                "includeFoodsOnHand": True,
                "includeToolsOnHand": True,
                "limit": 10,
                "foods": [str(user_food_1.id), str(user_food_2.id)],
                "tools": [str(user_tool_1.id)],
            },
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == len(recipes)
        for i, (item, recipe) in enumerate(zip(data["items"], recipes, strict=True)):
            try:
                assert item["recipe"]["id"] == str(recipe.id)
            except AssertionError as e:
                raise AssertionError(f"Recipe in position {i} was incorrect") from e

    finally:
        for recipe in recipes:
            unique_user.repos.recipes.delete(recipe.slug)


def test_respect_user_sort(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)

    # Create recipes with names A, B, C, D out of order
    recipe_b = create_recipe(unique_user, foods=[known_food], name="B")
    recipe_c = create_recipe(unique_user, foods=[known_food, create_food(unique_user)], name="C")
    recipe_a = create_recipe(unique_user, foods=[known_food, create_food(unique_user)], name="A")
    recipe_d = create_recipe(unique_user, foods=[known_food, create_food(unique_user)], name="D")

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 1, "foods": [str(known_food.id)], "orderBy": "name", "orderDirection": "desc"},
            headers=unique_user.token,
        )
        response.raise_for_status()

        data = response.json()
        assert len(data["items"]) == 4

        # "B" should come first because it matches all foods, even though the user sort would put it last
        assert [item["recipe"]["name"] for item in data["items"]] == ["B", "D", "C", "A"]

    finally:
        for recipe in [recipe_a, recipe_b, recipe_c, recipe_d]:
            unique_user.repos.recipes.delete(recipe.slug)


def test_limit_param(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    limit = random_int(12, 20)
    recipes = [create_recipe(unique_user, foods=[known_food]) for _ in range(limit)]

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "foods": [str(known_food.id)], "limit": limit},
            headers=unique_user.token,
        )
        response.raise_for_status()
        assert len(response.json()["items"]) == limit

    finally:
        for recipe in recipes:
            unique_user.repos.recipes.delete(recipe.slug)


def test_query_filter(api_client: TestClient, unique_user: TestUser):
    known_food = create_food(unique_user)
    recipes_with_prefix = [
        create_recipe(unique_user, foods=[known_food], name=f"MY_PREFIX{random_string()}") for _ in range(10)
    ]
    recipes_without_prefix = [
        create_recipe(unique_user, foods=[known_food], name=f"MY_OTHER_PREFIX{random_string()}") for _ in range(10)
    ]

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "foods": [str(known_food.id)], "queryFilter": 'name LIKE "MY_PREFIX%"'},
            headers=unique_user.token,
        )
        response.raise_for_status()
        assert len(response.json()["items"]) == len(recipes_with_prefix)
        assert {item["recipe"]["id"] for item in response.json()["items"]} == {
            str(recipe.id) for recipe in recipes_with_prefix
        }

    finally:
        for recipe in recipes_with_prefix + recipes_without_prefix:
            unique_user.repos.recipes.delete(recipe.slug)


def test_include_cross_household_recipes(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    known_food = create_food(unique_user)
    recipe = create_recipe(unique_user, foods=[known_food])
    other_recipe = create_recipe(h2_user, foods=[known_food])

    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "foods": [str(known_food.id)]},
            headers=h2_user.token,
        )
        response.raise_for_status()
        data = response.json()
        assert len(data["items"]) == 2
        assert {item["recipe"]["id"] for item in data["items"]} == {str(recipe.id), str(other_recipe.id)}

    finally:
        unique_user.repos.recipes.delete(recipe.slug)
        h2_user.repos.recipes.delete(other_recipe.slug)


def test_respect_cross_household_on_hand_food(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    on_hand_food = create_food(unique_user, on_hand=True)  # only on-hand for unique_user
    other_food = create_food(unique_user)

    recipe = create_recipe(unique_user, foods=[on_hand_food, other_food])
    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "foods": [str(other_food.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["recipe"]["id"] == str(recipe.id)

        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingFoods": 0, "foods": [str(other_food.id)]},
            headers=h2_user.token,
        )
        response.raise_for_status()
        data = response.json()
        assert len(data["items"]) == 0

    finally:
        unique_user.repos.recipes.delete(recipe.slug)


def test_respect_cross_household_on_hand_tool(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    on_hand_tool = create_tool(unique_user, on_hand=True)  # only on-hand for unique_user
    other_tool = create_tool(unique_user)

    recipe = create_recipe(unique_user, tools=[on_hand_tool, other_tool])
    try:
        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingTools": 0, "tools": [str(other_tool.id)]},
            headers=unique_user.token,
        )
        response.raise_for_status()
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["recipe"]["id"] == str(recipe.id)

        response = api_client.get(
            api_routes.recipes_suggestions,
            params={"maxMissingTools": 0, "tools": [str(other_tool.id)]},
            headers=h2_user.token,
        )
        response.raise_for_status()
        data = response.json()
        assert len(data["items"]) == 0

    finally:
        unique_user.repos.recipes.delete(recipe.slug)
