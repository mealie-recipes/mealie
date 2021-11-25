import json

import pytest
from fastapi.testclient import TestClient

from tests.utils.app_routes import AppRoutes


@pytest.fixture
def backup_data():
    return {
        "name": "test_backup_2021-Apr-27.zip",
        "force": True,
        "recipes": True,
        "settings": False,  # ! Broken
        "groups": False,  # ! Also Broken
        "users": False,
    }


def test_import(api_client: TestClient, api_routes: AppRoutes, backup_data, admin_token):
    import_route = api_routes.backups_file_name_import("test_backup_2021-Apr-27.zip")
    response = api_client.post(import_route, json=backup_data, headers=admin_token)
    assert response.status_code == 200
    for _, value in json.loads(response.content).items():
        for v in value:
            assert v["status"] is True
