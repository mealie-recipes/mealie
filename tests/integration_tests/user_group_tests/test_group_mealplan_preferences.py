from fastapi.testclient import TestClient

from mealie.repos.all_repositories import AllRepositories
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/categories"

    @staticmethod
    def item(item_id: int | str) -> str:
        return f"{Routes.base}/{item_id}"


def test_group_mealplan_set_preferences(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    # Create Categories
    categories = [{"name": x} for x in ["Breakfast", "Lunch", "Dinner"]]

    created = []
    for category in categories:
        create = database.categories.create(category)
        created.append(create.dict())

    # Set Category Preferences
    response = api_client.put(Routes.base, json=created, headers=unique_user.token)
    assert response.status_code == 200

    # Get Category Preferences
    response = api_client.get(Routes.base, headers=unique_user.token)
    assert response.status_code == 200

    as_dict = response.json()

    assert len(as_dict) == len(categories)

    for api_data, expected in zip(as_dict, created):
        assert_ignore_keys(api_data, expected, ["id", "recipes"])
