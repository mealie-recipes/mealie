from fastapi.testclient import TestClient

from mealie.schema.group.group_preferences import UpdateGroupPreferences
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


def test_get_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_preferences, headers=unique_user.token)
    assert response.status_code == 200

    preferences = response.json()

    assert preferences["privateGroup"] in {True, False}


def test_preferences_in_group(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_self, headers=unique_user.token)

    assert response.status_code == 200

    group = response.json()

    assert group["preferences"] is not None

    # Spot Check
    assert group["preferences"]["privateGroup"] in {True, False}


def test_update_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    new_data = UpdateGroupPreferences(private_group=random_bool())

    response = api_client.put(api_routes.groups_preferences, json=new_data.model_dump(), headers=unique_user.token)

    assert response.status_code == 200

    preferences = response.json()

    assert preferences is not None
    assert preferences["privateGroup"] == new_data.private_group

    assert_ignore_keys(new_data.model_dump(by_alias=True), preferences, ["id", "groupId"])
