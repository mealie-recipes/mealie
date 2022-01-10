from fastapi.testclient import TestClient

from mealie.services.server_tasks.background_executory import BackgroundExecutor
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/admin/server-tasks"


def test_admin_server_tasks_test_and_get(api_client: TestClient, admin_user: TestUser):
    # Bootstrap Timer
    BackgroundExecutor.sleep_time = 0.1

    response = api_client.post(Routes.base, headers=admin_user.token)
    assert response.status_code == 201

    response = api_client.get(Routes.base, headers=admin_user.token)
    as_dict = response.json()

    assert len(as_dict) == 1

    # Reset Timer
    BackgroundExecutor.sleep_time = 60
