from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_get_public(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_public, headers=unique_user.token)
    assert response.status_code == 200

    groups = response.json()

    assert len(groups) > 0
