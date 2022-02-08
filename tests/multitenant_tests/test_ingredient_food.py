from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood, SaveIngredientUnit
from tests import utils
from tests.fixtures.fixture_multitenant import MultiTenant
from tests.utils import routes


def test_foods_are_private_by_group(
    api_client: TestClient, multitenants: MultiTenant, database: AllRepositories
) -> None:
    user1 = multitenants.user_one
    user2 = multitenants.user_two

    # Bootstrap foods for user1
    food_ids: set[int] = set()
    for _ in range(10):
        food = database.ingredient_foods.create(
            SaveIngredientFood(
                group_id=user1.group_id,
                name=utils.random_string(10),
            )
        )

        food_ids.add(food.id)

    expected_results = [
        (user1.token, food_ids),
        (user2.token, []),
    ]

    for token, expected_food_ids in expected_results:
        response = api_client.get(routes.RoutesFoods.base, headers=token)
        assert response.status_code == 200

        data = response.json()

        assert len(data) == len(expected_food_ids)

        if len(data) > 0:
            for food in data:
                assert food["id"] in expected_food_ids


def test_units_are_private_by_group(
    api_client: TestClient, multitenants: MultiTenant, database: AllRepositories
) -> None:
    user1 = multitenants.user_one
    user2 = multitenants.user_two

    # Bootstrap foods for user1
    unit_ids: set[int] = set()
    for _ in range(10):
        food = database.ingredient_units.create(
            SaveIngredientUnit(
                group_id=user1.group_id,
                name=utils.random_string(10),
            )
        )

        unit_ids.add(food.id)

    expected_results = [
        (user1.token, unit_ids),
        (user2.token, []),
    ]

    for token, expected_unit_ids in expected_results:
        response = api_client.get(routes.RoutesUnits.base, headers=token)
        assert response.status_code == 200

        data = response.json()

        assert len(data) == len(expected_unit_ids)

        if len(data) > 0:
            for food in data:
                assert food["id"] in expected_unit_ids
