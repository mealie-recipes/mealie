import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from mealie.core.config import app_dirs
from tests.app_routes import AppRoutes
from tests.test_config import TEST_CHOWDOWN_DIR, TEST_NEXTCLOUD_DIR


@pytest.fixture(scope="session")
def chowdown_zip():
    zip = TEST_CHOWDOWN_DIR.joinpath("test_chowdown-gh-pages.zip")

    zip_copy = TEST_CHOWDOWN_DIR.joinpath("chowdown-gh-pages.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_chowdown_zip(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, token):
    upload_url = api_routes.migrations_import_type_upload("chowdown")
    response = api_client.post(upload_url, files={"archive": chowdown_zip.open("rb")}, headers=token)

    assert response.status_code == 200

    assert app_dirs.MIGRATION_DIR.joinpath("chowdown", chowdown_zip.name).is_file()


def test_import_chowdown_directory(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, token):
    delete_url = api_routes.recipes_recipe_slug("roasted-okra")
    api_client.delete(delete_url, headers=token)  # TODO: Manage Test Data better
    selection = chowdown_zip.name

    import_url = api_routes.migrations_import_type_file_name_import("chowdown", selection)
    response = api_client.post(import_url, headers=token)

    assert response.status_code == 200

    reports = json.loads(response.content)

    for report in reports:
        assert report.get("status") is True


def test_delete_chowdown_migration_data(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, token):
    selection = chowdown_zip.name
    delete_url = api_routes.migrations_import_type_file_name_delete("chowdown", selection)
    response = api_client.delete(delete_url, headers=token)

    assert response.status_code == 200
    assert not app_dirs.MIGRATION_DIR.joinpath(chowdown_zip.name).is_file()


# Nextcloud
@pytest.fixture(scope="session")
def nextcloud_zip():
    zip = TEST_NEXTCLOUD_DIR.joinpath("nextcloud.zip")

    zip_copy = TEST_NEXTCLOUD_DIR.joinpath("new_nextcloud.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_nextcloud_zip(api_client: TestClient, api_routes: AppRoutes, nextcloud_zip, token):
    upload_url = api_routes.migrations_import_type_upload("nextcloud")
    response = api_client.post(upload_url, files={"archive": nextcloud_zip.open("rb")}, headers=token)

    assert response.status_code == 200

    assert app_dirs.MIGRATION_DIR.joinpath("nextcloud", nextcloud_zip.name).is_file()


def test_import_nextcloud_directory(api_client: TestClient, api_routes: AppRoutes, nextcloud_zip, token):
    selection = nextcloud_zip.name
    import_url = api_routes.migrations_import_type_file_name_import("nextcloud", selection)
    response = api_client.post(import_url, headers=token)

    assert response.status_code == 200

    reports = json.loads(response.content)
    for report in reports:
        assert report.get("status") is True


def test_delete__nextcloud_migration_data(api_client: TestClient, api_routes: AppRoutes, nextcloud_zip: Path, token):
    selection = nextcloud_zip.name
    delete_url = api_routes.migrations_import_type_file_name_delete("nextcloud", selection)
    response = api_client.delete(delete_url, headers=token)

    assert response.status_code == 200
    assert not app_dirs.MIGRATION_DIR.joinpath(nextcloud_zip.name).is_file()
