from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False])
def test_get_group_preferences(api_client: TestClient, unique_user: TestUser, is_private_group: bool):
    unique_user.repos.group_preferences.patch(UUID(unique_user.group_id), {"private_group": is_private_group})
    response = api_client.get(api_routes.explore_groups_group_slug_preferences(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert response.json()["groupId"] == str(unique_user.group_id)
