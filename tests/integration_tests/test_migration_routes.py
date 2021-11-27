from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.test_config import TEST_CHOWDOWN_DIR, TEST_NEXTCLOUD_DIR
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/migrations"

    @staticmethod
    def report(item_id: str) -> str:
        return f"/api/groups/reports/{item_id}"


@pytest.mark.parametrize(
    "m_type, zip_path",
    [
        ("nextcloud", TEST_NEXTCLOUD_DIR.joinpath("nextcloud.zip")),
        ("chowdown", TEST_CHOWDOWN_DIR.joinpath("test_chowdown-gh-pages.zip")),
    ],
)
def test_migration_nextcloud(api_client: TestClient, zip_path: Path, m_type: str, unique_user: TestUser):
    payload = {
        "archive": zip_path.read_bytes(),
    }

    data = {
        "migration_type": m_type,
    }

    response = api_client.post(Routes.base, data=data, files=payload, headers=unique_user.token)

    assert response.status_code == 200

    id = response.json()["id"]

    response = api_client.get(Routes.report(id), headers=unique_user.token)

    assert response.status_code == 200

    report = response.json()

    assert report.get("status") == "success"

    for entry in report.get("entries"):
        assert entry.get("success") is True
