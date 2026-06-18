from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.user.user import GroupInDB
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


def test_home_group_not_deletable(api_client: TestClient, admin_user: TestUser):
    response = api_client.delete(api_routes.admin_groups_item_id(admin_user.group_id), headers=admin_user.token)
    assert response.status_code == 400


def test_admin_group_routes_are_restricted(api_client: TestClient, unique_user: TestUser, admin_user: TestUser):
    response = api_client.get(api_routes.admin_groups, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.post(api_routes.admin_groups, json={}, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_groups_item_id(admin_user.group_id), headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_users_item_id(admin_user.group_id), headers=unique_user.token)
    assert response.status_code == 403


def test_admin_create_group(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(api_routes.admin_groups, json={"name": random_string()}, headers=admin_user.token)
    assert response.status_code == 201

    # verify preferences are set and the default household is created
    group = GroupInDB.model_validate(response.json())
    assert group.preferences and len(group.households) == 1
    created_household = group.households[0]
    assert created_household.name == get_app_settings().DEFAULT_HOUSEHOLD

    response = api_client.get(api_routes.admin_households_item_id(created_household.id), headers=admin_user.token)
    assert response.status_code == 200
    assert response.json()["id"] == str(created_household.id)

    # verify no extra households are created
    response = api_client.get(api_routes.admin_households, headers=admin_user.token, params={"page": 1, "perPage": -1})
    assert response.status_code == 200
    items = response.json()["items"]
    filtered_item_ids: list[str] = []
    for item in items:
        if item["groupId"] == str(group.id):
            filtered_item_ids.append(item["id"])

    assert len(filtered_item_ids) == 1
    assert filtered_item_ids[0] == str(created_household.id)


def test_admin_update_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    update_payload = {
        "id": unique_user.group_id,
        "name": "New Name",
        "preferences": {
            "privateGroup": random_bool(),
            "showAnnouncements": random_bool(),
        },
    }

    response = api_client.put(
        api_routes.admin_groups_item_id(unique_user.group_id),
        json=update_payload,
        headers=admin_user.token,
    )

    assert response.status_code == 200

    as_json = response.json()

    assert as_json["name"] == update_payload["name"]
    assert_ignore_keys(as_json["preferences"], update_payload["preferences"])  # type: ignore


def test_admin_update_group_name_only(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Updating only the name leaves preferences and ai_provider_settings untouched."""
    new_name = random_string()
    response = api_client.put(
        api_routes.admin_groups_item_id(unique_user.group_id),
        json={"id": unique_user.group_id, "name": new_name},
        headers=admin_user.token,
    )
    assert response.status_code == 200
    assert response.json()["name"] == new_name


def test_admin_update_group_ai_provider_settings(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can update ai_provider_settings for a group via the PUT endpoint."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    try:
        update_payload = {
            "id": unique_user.group_id,
            "name": unique_user.group_id,  # name is required but unchanged
            "aiProviderSettings": {
                "defaultProviderId": str(provider.id),
                "audioProviderId": str(provider.id),
                "imageProviderId": str(provider.id),
            },
        }
        response = api_client.put(
            api_routes.admin_groups_item_id(unique_user.group_id),
            json=update_payload,
            headers=admin_user.token,
        )
        assert response.status_code == 200

        settings = response.json()["aiProviderSettings"]
        assert settings["defaultProviderId"] == str(provider.id)
        assert settings["audioProviderId"] == str(provider.id)
        assert settings["imageProviderId"] == str(provider.id)
    finally:
        # Clear provider references before deleting the provider
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        unique_user.repos.group_ai_providers.delete(provider.id)


def test_admin_update_group_ai_provider_settings_clear(
    api_client: TestClient, admin_user: TestUser, unique_user: TestUser
):
    """Admin can clear ai_provider_settings provider IDs for a group."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    try:
        # First set the providers
        api_client.put(
            api_routes.admin_groups_item_id(unique_user.group_id),
            json={
                "id": unique_user.group_id,
                "name": unique_user.group_id,
                "aiProviderSettings": {
                    "defaultProviderId": str(provider.id),
                    "audioProviderId": None,
                    "imageProviderId": None,
                },
            },
            headers=admin_user.token,
        )

        # Now clear them
        response = api_client.put(
            api_routes.admin_groups_item_id(unique_user.group_id),
            json={
                "id": unique_user.group_id,
                "name": unique_user.group_id,
                "aiProviderSettings": {
                    "defaultProviderId": None,
                    "audioProviderId": None,
                    "imageProviderId": None,
                },
            },
            headers=admin_user.token,
        )
        assert response.status_code == 200

        settings = response.json()["aiProviderSettings"]
        assert settings["defaultProviderId"] is None
        assert settings["audioProviderId"] is None
        assert settings["imageProviderId"] is None
    finally:
        unique_user.repos.group_ai_providers.delete(provider.id)


def test_admin_delete_group(unfiltered_database: AllRepositories, api_client: TestClient, admin_user: TestUser):
    group = unfiltered_database.groups.create({"name": random_string()})
    response = api_client.delete(api_routes.admin_groups_item_id(group.id), headers=admin_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.admin_groups_item_id(group.id), headers=admin_user.token)
    assert response.status_code == 404
