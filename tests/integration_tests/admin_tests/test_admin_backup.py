from fastapi.testclient import TestClient

from mealie.core.config import get_app_dirs
from tests import data
from tests.utils.fixture_schemas import TestUser


def test_recipe_asset_exploit(api_client: TestClient, admin_user: TestUser):
    dirs = get_app_dirs()

    file_payload = {
        "archive": ("../test.txt", data.images_test_image_1.read_bytes()),
    }

    response = api_client.post(
        "/api/admin/backups/upload",
        files=file_payload,
        headers=admin_user.token,
    )

    assert response.status_code == 400

    # Ensure File was not created
    assert not (dirs.BACKUP_DIR / "test.txt").exists()
    assert not (dirs.BACKUP_DIR.parent / "test.txt").exists()
