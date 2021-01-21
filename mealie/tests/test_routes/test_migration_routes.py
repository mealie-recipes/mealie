import json
import shutil

import pytest
from app_config import MIGRATION_DIR
from tests.test_config import TEST_NEXTCLOUD_DIR

#! Broken
# def test_import_chowdown_recipes(api_client):
#     response = api_client.post(
#         "/api/migration/chowdown/repo/",
#         json={"url": "https://github.com/hay-kot/chowdown"},
#     )

#     assert response.status_code == 200

#     test_slug = "banana-bread"
#     response = api_client.get(f"/api/recipe/{test_slug}/")
#     assert response.status_code == 200

#     recipe = json.loads(response.content)
#     assert recipe["slug"] == test_slug


@pytest.fixture(scope="session")
def nextcloud_zip():
    zip = TEST_NEXTCLOUD_DIR.joinpath("nextcloud.zip")

    zip_copy = TEST_NEXTCLOUD_DIR.joinpath("new_nextcloud.zip")

    shutil.copy(zip, zip_copy)

    return zip_copy


def test_upload_nextcloud_zip(api_client, nextcloud_zip):

    response = api_client.post(
        "/api/migration/upload/", files={"archive": nextcloud_zip.open("rb")}
    )

    assert response.status_code == 200

    assert MIGRATION_DIR.joinpath(nextcloud_zip.name).is_file()


def test_import_nextcloud_directory(api_client, nextcloud_zip):
    selection = nextcloud_zip.name
    response = api_client.post(f"/api/migration/nextcloud/{selection}/import/")

    assert response.status_code == 200

    report = json.loads(response.content)
    assert report["failed"] == []

    expected_slug = "air-fryer-shrimp"
    response = api_client.get(f"/api/recipe/{expected_slug}/")
    assert response.status_code == 200


def test_delete_migration_data(api_client, nextcloud_zip):
    selection = nextcloud_zip.name
    response = api_client.delete(f"/api/migration/{selection}/delete/")

    assert response.status_code == 200
    assert not MIGRATION_DIR.joinpath(nextcloud_zip.name).is_file()
