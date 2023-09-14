import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False], ids=["group_is_private", "group_is_public"])
def test_get_all_foods(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    is_private_group: bool,
):
    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Foods
    foods = database.ingredient_foods.create_many(
        [SaveIngredientFood(name=random_string(), group_id=unique_user.group_id) for _ in range(random_int(15, 20))]
    )

    ## Test Foods
    response = api_client.get(api_routes.explore_foods_group_slug(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    foods_data = response.json()
    fetched_ids: set[str] = {food["id"] for food in foods_data["items"]}

    for food in foods:
        assert str(food.id) in fetched_ids


@pytest.mark.parametrize("is_private_group", [True, False], ids=["group_is_private", "group_is_public"])
def test_get_one_food(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    is_private_group: bool,
):
    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Food
    food = database.ingredient_foods.create(SaveIngredientFood(name=random_string(), group_id=unique_user.group_id))

    ## Test Food
    response = api_client.get(api_routes.explore_foods_group_slug_item_id(unique_user.group_id, food.id))
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    food_data = response.json()
    assert food_data["id"] == str(food.id)
