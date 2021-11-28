from uuid import UUID

from fastapi.testclient import TestClient

from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/cookbooks"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


def get_page_data(group_id: UUID):
    return {
        "name": "My New Page",
        "slug": "my-new-page",
        "description": "",
        "position": 0,
        "categories": [],
        "group_id": group_id,
    }


def test_create_cookbook(api_client: TestClient, unique_user: TestUser):
    page_data = get_page_data(unique_user.group_id)
    response = api_client.post(Routes.base, json=page_data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_cookbook(api_client: TestClient, unique_user: TestUser):
    page_data = get_page_data(unique_user.group_id)

    response = api_client.get(Routes.item(1), headers=unique_user.token)
    assert_ignore_keys(response.json(), page_data)


def test_update_cookbook(api_client: TestClient, unique_user: TestUser):
    page_data = get_page_data(unique_user.group_id)

    page_data["id"] = 1
    page_data["name"] = "My New Name"

    response = api_client.put(Routes.item(1), json=page_data, headers=unique_user.token)

    assert response.status_code == 200


def test_delete_cookbook(api_client: TestClient, unique_user: TestUser):
    response = api_client.delete(Routes.item(1), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(1), headers=unique_user.token)
    assert response.status_code == 404
