"""
Integration tests for admin AI provider management across groups.
"""

from fastapi.testclient import TestClient

from mealie.schema.group.ai_providers import AIProviderCreate
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# =======================================================================
# Permissions


def test_admin_ai_provider_routes_require_admin(api_client: TestClient, unique_user: TestUser, admin_user: TestUser):
    """Non-admin users cannot access admin AI provider routes."""
    group_id = unique_user.group_id

    response = api_client.post(
        api_routes.admin_groups_group_id_ai_providers_providers(group_id),
        json={"name": random_string(), "model": "gpt-4o", "apiKey": "key"},
        headers=unique_user.token,
    )
    assert response.status_code == 403


# =======================================================================
# Provider CRUD


def test_admin_create_ai_provider_for_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can create an AI provider for any group."""
    provider_name = random_string()
    response = api_client.post(
        api_routes.admin_groups_group_id_ai_providers_providers(unique_user.group_id),
        json={"name": provider_name, "model": "gpt-4o", "apiKey": "admin-created-key"},
        headers=admin_user.token,
    )
    assert response.status_code == 200

    provider = response.json()
    try:
        assert provider["name"] == provider_name
        assert provider["model"] == "gpt-4o"
        assert "id" in provider
        assert "apiKey" not in provider
    finally:
        unique_user.repos.group_ai_providers.delete(provider["id"])


def test_admin_get_ai_provider_for_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can retrieve an AI provider from any group."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="secret")
    )
    try:
        response = api_client.get(
            api_routes.admin_groups_group_id_ai_providers_providers_provider_id(unique_user.group_id, provider.id),
            headers=admin_user.token,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(provider.id)
        assert data["name"] == provider.name
    finally:
        unique_user.repos.group_ai_providers.delete(provider.id)


def test_admin_update_ai_provider_for_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can update an AI provider in any group."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="original-key")
    )
    try:
        new_name = random_string()
        response = api_client.put(
            api_routes.admin_groups_group_id_ai_providers_providers_provider_id(unique_user.group_id, provider.id),
            json={"name": new_name, "model": "gpt-4-turbo", "apiKey": "updated-key"},
            headers=admin_user.token,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == new_name
        assert data["model"] == "gpt-4-turbo"
    finally:
        unique_user.repos.group_ai_providers.delete(provider.id)


def test_admin_delete_ai_provider_for_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can delete an AI provider from any group."""
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="to-delete")
    )

    response = api_client.delete(
        api_routes.admin_groups_group_id_ai_providers_providers_provider_id(unique_user.group_id, provider.id),
        headers=admin_user.token,
    )
    assert response.status_code == 200

    # Confirm gone
    response = api_client.get(
        api_routes.admin_groups_group_id_ai_providers_providers_provider_id(unique_user.group_id, provider.id),
        headers=admin_user.token,
    )
    assert response.status_code == 404


def test_admin_can_manage_providers_across_groups(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    """Admin can create providers in a group they are not a member of."""
    # Create a brand new group the admin doesn't belong to
    group_name = random_string()
    create_resp = api_client.post(api_routes.admin_groups, json={"name": group_name}, headers=admin_user.token)
    assert create_resp.status_code == 201
    foreign_group_id = create_resp.json()["id"]

    try:
        response = api_client.post(
            api_routes.admin_groups_group_id_ai_providers_providers(foreign_group_id),
            json={"name": random_string(), "model": "gpt-4o", "apiKey": "cross-group-key"},
            headers=admin_user.token,
        )
        assert response.status_code == 200
        provider_id = response.json()["id"]

        # Settings should also be accessible
        # Cleanup provider before deleting group
        api_client.delete(
            api_routes.admin_groups_group_id_ai_providers_providers_provider_id(foreign_group_id, provider_id),
            headers=admin_user.token,
        )
    finally:
        api_client.delete(api_routes.admin_groups_item_id(foreign_group_id), headers=admin_user.token)
