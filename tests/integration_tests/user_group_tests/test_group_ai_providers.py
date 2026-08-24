"""
Integration tests for AI provider CRUD, settings, permissions, and API key security.
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from tests.utils import api_routes
from tests.utils.factories import random_string, user_registration_factory
from tests.utils.fixture_schemas import TestUser

# ==========================================
# Provider CRUD
# ==========================================


def test_create_provider(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(), "model": "gpt-4o", "apiKey": "test-key"}
    response = api_client.post(api_routes.groups_ai_providers_providers, json=data, headers=unique_user.token)
    assert response.status_code == 200

    provider = response.json()
    assert provider["name"] == data["name"]
    assert provider["model"] == data["model"]
    assert "id" in provider

    api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider["id"]), headers=unique_user.token)


def test_get_provider(api_client: TestClient, unique_user: TestUser):
    # Create a provider first
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        response = api_client.get(
            api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(provider.id)
        assert data["name"] == provider.name
        assert data["model"] == provider.model
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_get_provider_not_found(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.groups_ai_providers_providers_provider_id(uuid4()), headers=unique_user.token)
    assert response.status_code == 404


def test_update_provider(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="original-key")
    )

    try:
        new_model = "gpt-4-turbo"
        update_data = {"name": provider.name, "model": new_model, "apiKey": "updated-key"}
        response = api_client.put(
            api_routes.groups_ai_providers_providers_provider_id(provider.id),
            json=update_data,
            headers=unique_user.token,
        )
        assert response.status_code == 200

        updated = response.json()
        assert updated["model"] == new_model
        assert updated["id"] == str(provider.id)
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_delete_provider(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    response = api_client.delete(
        api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token
    )
    assert response.status_code == 200

    # Verify it's gone
    response = api_client.get(
        api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token
    )
    assert response.status_code == 404


# ==========================================
# Provider Settings CRUD
# ==========================================


def test_get_settings(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.groups_ai_providers_settings, headers=unique_user.token)
    assert response.status_code == 200

    settings = response.json()
    assert "providers" in settings
    assert "defaultProviderId" in settings
    assert "audioProviderId" in settings
    assert "imageProviderId" in settings


def test_update_settings_set_default_provider(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        update = {"defaultProviderId": str(provider.id), "audioProviderId": None, "imageProviderId": None}
        response = api_client.put(api_routes.groups_ai_providers_settings, json=update, headers=unique_user.token)
        assert response.status_code == 200

        settings = response.json()
        assert settings["defaultProviderId"] == str(provider.id)
    finally:
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_update_settings_all_provider_types(api_client: TestClient, unique_user: TestUser):
    default_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    audio_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="whisper-1", api_key="test-key")
    )
    image_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="dall-e-3", api_key="test-key")
    )

    try:
        update = {
            "defaultProviderId": str(default_provider.id),
            "audioProviderId": str(audio_provider.id),
            "imageProviderId": str(image_provider.id),
        }
        response = api_client.put(api_routes.groups_ai_providers_settings, json=update, headers=unique_user.token)
        assert response.status_code == 200

        settings = response.json()
        assert settings["defaultProviderId"] == str(default_provider.id)
        assert settings["audioProviderId"] == str(audio_provider.id)
        assert settings["imageProviderId"] == str(image_provider.id)
    finally:
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        for p in [default_provider, audio_provider, image_provider]:
            api_client.delete(api_routes.groups_ai_providers_providers_provider_id(p.id), headers=unique_user.token)


def test_update_settings_clear_providers(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=provider.id, audio_provider_id=None, image_provider_id=None),
    )

    try:
        # Now clear all
        update = {"defaultProviderId": None, "audioProviderId": None, "imageProviderId": None}
        response = api_client.put(api_routes.groups_ai_providers_settings, json=update, headers=unique_user.token)
        assert response.status_code == 200

        settings = response.json()
        assert settings["defaultProviderId"] is None
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_settings_providers_list_populated(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        response = api_client.get(api_routes.groups_ai_providers_settings, headers=unique_user.token)
        assert response.status_code == 200

        provider_ids = [p["id"] for p in response.json()["providers"]]
        assert str(provider.id) in provider_ids
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


# ==========================================
# Delete provider cascades to settings
# ==========================================


def test_delete_default_provider_clears_settings(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=provider.id, audio_provider_id=None, image_provider_id=None),
    )

    # Delete the provider
    response = api_client.delete(
        api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token
    )
    assert response.status_code == 200

    # Settings should now have nulled-out default
    settings = unique_user.repos.group_ai_provider_settings.get_one(unique_user.repos.group_id)
    assert settings is not None
    assert settings.default_provider_id is None


def test_delete_audio_provider_clears_settings(api_client: TestClient, unique_user: TestUser):
    default_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    audio_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="whisper-1", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=default_provider.id,
            audio_provider_id=audio_provider.id,
            image_provider_id=None,
        ),
    )

    try:
        # Delete only the audio provider
        api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(audio_provider.id), headers=unique_user.token
        )

        settings = unique_user.repos.group_ai_provider_settings.get_one(unique_user.repos.group_id)
        assert settings is not None
        assert settings.audio_provider_id is None
        assert settings.default_provider_id == default_provider.id
    finally:
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(default_provider.id), headers=unique_user.token
        )


def test_delete_image_provider_clears_settings(api_client: TestClient, unique_user: TestUser):
    default_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    image_provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="dall-e-3", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=default_provider.id,
            audio_provider_id=None,
            image_provider_id=image_provider.id,
        ),
    )

    try:
        # Delete only the image provider
        api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(image_provider.id), headers=unique_user.token
        )

        settings = unique_user.repos.group_ai_provider_settings.get_one(unique_user.repos.group_id)
        assert settings is not None
        assert settings.image_provider_id is None
        assert settings.default_provider_id == default_provider.id
    finally:
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(default_provider.id), headers=unique_user.token
        )


# ==========================================
# Permissions: can_manage required
# ==========================================


def test_providers_require_can_manage_get(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    # Ensure user does NOT have can_manage
    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    # Create a provider so there's something to GET (using repos directly to bypass permission check)
    provider = usr.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        response = api_client.get(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=usr.token)
        assert response.status_code == 403
    finally:
        usr.repos.group_ai_providers.delete(provider.id)


def test_providers_require_can_manage_create(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    data = {"name": random_string(), "model": "gpt-4o", "apiKey": "test-key"}
    response = api_client.post(api_routes.groups_ai_providers_providers, json=data, headers=usr.token)
    assert response.status_code == 403


def test_providers_require_can_manage_update(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    provider = usr.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        update_data = {"name": provider.name, "model": "gpt-4-turbo", "apiKey": "key"}
        response = api_client.put(
            api_routes.groups_ai_providers_providers_provider_id(provider.id), json=update_data, headers=usr.token
        )
        assert response.status_code == 403
    finally:
        usr.repos.group_ai_providers.delete(provider.id)


def test_providers_require_can_manage_delete(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    provider = usr.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )

    try:
        response = api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=usr.token
        )
        assert response.status_code == 403
    finally:
        usr.repos.group_ai_providers.delete(provider.id)


def test_settings_require_can_manage_get(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    response = api_client.get(api_routes.groups_ai_providers_settings, headers=usr.token)
    assert response.status_code == 403


def test_settings_require_can_manage_update(api_client: TestClient, user_tuple: list[TestUser]):
    usr, _ = user_tuple

    user = usr.repos.users.get_one(usr.user_id)
    assert user
    user.can_manage = False
    usr.repos.users.update(user.id, user)

    update = {"defaultProviderId": None, "audioProviderId": None, "imageProviderId": None}
    response = api_client.put(api_routes.groups_ai_providers_settings, json=update, headers=usr.token)
    assert response.status_code == 403


# ==========================================
# API key not exposed in responses
# ==========================================


def test_api_key_not_in_create_response(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(), "model": "gpt-4o", "apiKey": "super-secret-key"}
    response = api_client.post(api_routes.groups_ai_providers_providers, json=data, headers=unique_user.token)
    assert response.status_code == 200

    provider = response.json()
    try:
        assert "apiKey" not in provider
        assert "api_key" not in provider
        assert "super-secret-key" not in str(provider)
    finally:
        api_client.delete(
            api_routes.groups_ai_providers_providers_provider_id(provider["id"]), headers=unique_user.token
        )


def test_api_key_not_in_get_response(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="super-secret-key")
    )

    try:
        response = api_client.get(
            api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token
        )
        assert response.status_code == 200

        data = response.json()
        assert "apiKey" not in data
        assert "api_key" not in data
        assert "super-secret-key" not in str(data)
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_api_key_not_in_update_response(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="original-key")
    )

    try:
        update_data = {"name": provider.name, "model": "gpt-4-turbo", "apiKey": "updated-secret-key"}
        response = api_client.put(
            api_routes.groups_ai_providers_providers_provider_id(provider.id),
            json=update_data,
            headers=unique_user.token,
        )
        assert response.status_code == 200

        data = response.json()
        assert "apiKey" not in data
        assert "api_key" not in data
        assert "updated-secret-key" not in str(data)
        assert "original-key" not in str(data)
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_api_key_not_in_settings_response(api_client: TestClient, unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="secret-in-settings")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=provider.id, audio_provider_id=None, image_provider_id=None),
    )

    try:
        response = api_client.get(api_routes.groups_ai_providers_settings, headers=unique_user.token)
        assert response.status_code == 200

        data = response.json()
        assert "apiKey" not in data
        assert "api_key" not in data
        assert "secret-in-settings" not in str(data)
    finally:
        unique_user.repos.group_ai_provider_settings.update(
            unique_user.repos.group_id,
            AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
        )
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


def test_api_key_not_in_groups_self_response(api_client: TestClient, unique_user: TestUser):
    """Ensure the groups/self endpoint does not expose any AI provider data including API keys."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="groups-self-secret")
    )

    try:
        response = api_client.get(api_routes.groups_self, headers=unique_user.token)
        assert response.status_code == 200

        data = response.json()
        assert "api_key" not in str(data)
        assert "apiKey" not in str(data)
        assert "groups-self-secret" not in str(data)
    finally:
        api_client.delete(api_routes.groups_ai_providers_providers_provider_id(provider.id), headers=unique_user.token)


# ==========================================
# New group creation creates empty settings singleton
# ==========================================


def test_new_group_has_empty_ai_provider_settings(api_client: TestClient):
    """When a user registers (creating a new group), empty AI provider settings are created."""
    registration = user_registration_factory()
    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": registration.email, "password": registration.password}
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Fetch AI provider settings for the newly created group
    response = api_client.get(api_routes.groups_ai_providers_settings, headers=headers)
    assert response.status_code == 200

    settings = response.json()
    assert settings["defaultProviderId"] is None
    assert settings["audioProviderId"] is None
    assert settings["imageProviderId"] is None
    assert settings["providers"] == []


def test_new_group_created_via_admin_has_empty_ai_provider_settings(
    api_client: TestClient,
    admin_token: dict,
):
    """When an admin creates a group, empty AI provider settings are created."""
    group_name = random_string()
    response = api_client.post(api_routes.admin_groups, json={"name": group_name}, headers=admin_token)
    assert response.status_code == 201
    group_id = response.json()["id"]

    try:
        # Create a user in the new group with can_manage=True
        user_data = {
            "fullName": random_string(),
            "username": random_string(),
            "email": f"{random_string()}@example.com",
            "password": "useruser",
            "group": group_name,
            "household": "Family",
            "admin": False,
            "canManage": True,
            "tokens": [],
        }
        response = api_client.post(api_routes.admin_users, json=user_data, headers=admin_token)
        assert response.status_code == 201

        # Login as the new user
        form_data = {"username": user_data["email"], "password": "useruser"}
        response = api_client.post(api_routes.auth_token, data=form_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = api_client.get(api_routes.groups_ai_providers_settings, headers=headers)
        assert response.status_code == 200

        settings = response.json()
        assert settings["defaultProviderId"] is None
        assert settings["audioProviderId"] is None
        assert settings["imageProviderId"] is None
        assert settings["providers"] == []
    finally:
        api_client.delete(api_routes.admin_groups_item_id(group_id), headers=admin_token)
