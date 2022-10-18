from fastapi.testclient import TestClient

from mealie.services.server_tasks.background_executory import BackgroundExecutor
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_admin_server_tasks_test_and_get(api_client: TestClient, admin_user: TestUser):
    # Bootstrap Timer
    BackgroundExecutor.sleep_time = 1

    response = api_client.post(api_routes.admin_server_tasks, headers=admin_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.admin_server_tasks, headers=admin_user.token)
    as_dict = response.json()["items"]

    assert len(as_dict) == 1

    # Reset Timer
    BackgroundExecutor.sleep_time = 60
