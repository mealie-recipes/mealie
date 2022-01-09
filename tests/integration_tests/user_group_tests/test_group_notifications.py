from fastapi.testclient import TestClient

from mealie.schema.group.group_events import GroupEventNotifierCreate, GroupEventNotifierOptions
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/events/notifications"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


def preferences_generator():
    return GroupEventNotifierOptions(
        recipe_create=random_bool(),
        recipe_update=random_bool(),
        recipe_delete=random_bool(),
        user_signup=random_bool(),
        data_migrations=random_bool(),
        data_export=random_bool(),
        data_import=random_bool(),
        new_mealplan_entry=random_bool(),
        shopping_list_create=random_bool(),
        shopping_list_update=random_bool(),
        shopping_list_delete=random_bool(),
        cookbook_create=random_bool(),
        cookbook_update=random_bool(),
        cookbook_delete=random_bool(),
        tag_create=random_bool(),
        tag_update=random_bool(),
        tag_delete=random_bool(),
        category_create=random_bool(),
        category_update=random_bool(),
        category_delete=random_bool(),
    ).dict(by_alias=True)


def notifier_generator():
    return GroupEventNotifierCreate(
        name=random_string(),
        apprise_url=random_string(),
    ).dict(by_alias=True)


def test_create_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    assert payload_as_dict["name"] == payload["name"]
    assert payload_as_dict["enabled"] is True

    # Ensure Apprise URL Staysa Private
    assert "apprise_url" not in payload_as_dict

    # Cleanup
    response = api_client.delete(Routes.item(payload_as_dict["id"]), headers=unique_user.token)


def test_ensure_apprise_url_is_secret(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    # Ensure Apprise URL Staysa Private
    assert "apprise_url" not in payload_as_dict


def test_update_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    update_payload = response.json()

    # Set Update Values
    update_payload["name"] = random_string()
    update_payload["enabled"] = random_bool()
    update_payload["options"] = preferences_generator()

    response = api_client.put(Routes.item(update_payload["id"]), json=update_payload, headers=unique_user.token)

    assert response.status_code == 200

    # Re-Get The Item
    response = api_client.get(Routes.item(update_payload["id"]), headers=unique_user.token)
    assert response.status_code == 200

    # Validate Updated Values
    updated_payload = response.json()

    assert updated_payload["name"] == update_payload["name"]
    assert updated_payload["enabled"] == update_payload["enabled"]
    assert_ignore_keys(updated_payload["options"], update_payload["options"])

    # Cleanup
    response = api_client.delete(Routes.item(update_payload["id"]), headers=unique_user.token)


def test_delete_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    response = api_client.delete(Routes.item(payload_as_dict["id"]), headers=unique_user.token)
    assert response.status_code == 204

    response = api_client.get(Routes.item(payload_as_dict["id"]), headers=unique_user.token)
    assert response.status_code == 404
