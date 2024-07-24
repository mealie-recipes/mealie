from fastapi.testclient import TestClient

from mealie.schema.household.group_events import GroupEventNotifierCreate, GroupEventNotifierOptions
from mealie.services.event_bus_service.event_bus_listeners import AppriseEventListener
from mealie.services.event_bus_service.event_bus_service import Event
from mealie.services.event_bus_service.event_types import (
    EventBusMessage,
    EventDocumentDataBase,
    EventDocumentType,
    EventOperation,
    EventTypes,
)
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_email, random_int, random_string
from tests.utils.fixture_schemas import TestUser


def preferences_generator():
    return GroupEventNotifierOptions(
        recipe_created=random_bool(),
        recipe_updated=random_bool(),
        recipe_deleted=random_bool(),
        user_signup=random_bool(),
        data_migrations=random_bool(),
        data_export=random_bool(),
        data_import=random_bool(),
        mealplan_entry_created=random_bool(),
        shopping_list_created=random_bool(),
        shopping_list_updated=random_bool(),
        shopping_list_deleted=random_bool(),
        cookbook_created=random_bool(),
        cookbook_updated=random_bool(),
        cookbook_deleted=random_bool(),
        tag_created=random_bool(),
        tag_updated=random_bool(),
        tag_deleted=random_bool(),
        category_created=random_bool(),
        category_updated=random_bool(),
        category_deleted=random_bool(),
    ).model_dump(by_alias=True)


def notifier_generator():
    return GroupEventNotifierCreate(
        name=random_string(),
        apprise_url=random_string(),
    ).model_dump(by_alias=True)


def event_generator():
    return Event(
        message=EventBusMessage(title=random_string(), body=random_string()),
        event_type=EventTypes.test_message,
        integration_id=random_string(),
        document_data=EventDocumentDataBase(document_type=EventDocumentType.generic, operation=EventOperation.info),
    )


def test_create_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(api_routes.households_events_notifications, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    assert payload_as_dict["name"] == payload["name"]
    assert payload_as_dict["enabled"] is True

    # Ensure Apprise URL Stays Private
    assert "apprise_url" not in payload_as_dict

    # Cleanup
    response = api_client.delete(
        api_routes.households_events_notifications_item_id(payload_as_dict["id"]), headers=unique_user.token
    )


def test_ensure_apprise_url_is_secret(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(api_routes.households_events_notifications, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    # Ensure Apprise URL Staysa Private
    assert "apprise_url" not in payload_as_dict


def test_update_apprise_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(api_routes.households_events_notifications, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    update_payload = response.json()

    # Set Update Values
    update_payload["name"] = random_string()
    update_payload["enabled"] = random_bool()
    update_payload["options"] = preferences_generator()

    response = api_client.put(
        api_routes.households_events_notifications_item_id(update_payload["id"]),
        json=update_payload,
        headers=unique_user.token,
    )

    assert response.status_code == 200

    # Re-Get The Item
    response = api_client.get(
        api_routes.households_events_notifications_item_id(update_payload["id"]), headers=unique_user.token
    )
    assert response.status_code == 200

    # Validate Updated Values
    updated_payload = response.json()

    assert updated_payload["name"] == update_payload["name"]
    assert updated_payload["enabled"] == update_payload["enabled"]
    assert_ignore_keys(updated_payload["options"], update_payload["options"])

    # Cleanup
    response = api_client.delete(
        api_routes.households_events_notifications_item_id(update_payload["id"]), headers=unique_user.token
    )


def test_delete_apprise_notification(api_client: TestClient, unique_user: TestUser):
    payload = notifier_generator()
    response = api_client.post(api_routes.households_events_notifications, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    payload_as_dict = response.json()

    response = api_client.delete(
        api_routes.households_events_notifications_item_id(payload_as_dict["id"]), headers=unique_user.token
    )
    assert response.status_code == 204

    response = api_client.get(
        api_routes.households_events_notifications_item_id(payload_as_dict["id"]), headers=unique_user.token
    )
    assert response.status_code == 404


def test_apprise_event_bus_listener_functions():
    test_event = event_generator()

    test_standard_urls = [
        "a" + random_string(),
        f"ses://{random_email()}/{random_string()}/{random_string()}/us-east-1/",
        f"pBUL://{random_string()}/{random_email()}",
    ]

    test_custom_urls = [
        "JSON://" + random_string(),
        f"jsons://{random_string()}:my/pass/word@{random_string()}.com/{random_string()}",
        "form://" + random_string(),
        "fORMS://" + str(random_int()),
        "xml:" + str(random_int()),
        "xmls://" + random_string(),
    ]

    # Validate all standard urls are not considered custom
    responses = [AppriseEventListener.is_custom_url(url) for url in test_standard_urls]
    assert not any(responses)

    # Validate all custom urls are actually considered custom
    responses = [AppriseEventListener.is_custom_url(url) for url in test_custom_urls]
    assert all(responses)

    updated_standard_urls = AppriseEventListener.update_urls_with_event_data(test_standard_urls, test_event)
    updated_custom_urls = AppriseEventListener.update_urls_with_event_data(test_custom_urls, test_event)

    # Validate that no URLs are lost when updating them
    assert len(updated_standard_urls) == len(test_standard_urls)
    assert len(updated_custom_urls) == len(updated_custom_urls)
