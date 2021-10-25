import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from mealie.core.config import app_dirs
from tests.app_routes import AppRoutes
from tests.test_config import TEST_CHOWDOWN_DIR, TEST_NEXTCLOUD_DIR, TEST_CSV_DIR


@pytest.fixture(scope="session")
def chowdown_zip():
    zip = TEST_CHOWDOWN_DIR.joinpath("test_chowdown-gh-pages.zip")

    zip_copy = TEST_CHOWDOWN_DIR.joinpath("chowdown-gh-pages.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_chowdown_zip(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, admin_token):
    upload_url = api_routes.migrations_import_type_upload("chowdown")
    response = api_client.post(upload_url, files={"archive": chowdown_zip.open("rb")}, headers=admin_token)

    assert response.status_code == 200

    assert app_dirs.MIGRATION_DIR.joinpath("chowdown", chowdown_zip.name).is_file()


def test_import_chowdown_directory(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, admin_token):
    delete_url = api_routes.recipes_recipe_slug("roasted-okra")
    api_client.delete(delete_url, headers=admin_token)  # TODO: Manage Test Data better
    selection = chowdown_zip.name

    import_url = api_routes.migrations_import_type_file_name_import("chowdown", selection)
    response = api_client.post(import_url, headers=admin_token)

    assert response.status_code == 200

    reports = json.loads(response.content)

    for report in reports:
        assert report.get("status") is True


def test_delete_chowdown_migration_data(api_client: TestClient, api_routes: AppRoutes, chowdown_zip: Path, admin_token):
    selection = chowdown_zip.name
    delete_url = api_routes.migrations_import_type_file_name_delete("chowdown", selection)
    response = api_client.delete(delete_url, headers=admin_token)

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


def test_upload_nextcloud_zip(api_client: TestClient, api_routes: AppRoutes, nextcloud_zip, admin_token):
    upload_url = api_routes.migrations_import_type_upload("nextcloud")
    response = api_client.post(upload_url, files={"archive": nextcloud_zip.open("rb")}, headers=admin_token)

    assert response.status_code == 200

    assert app_dirs.MIGRATION_DIR.joinpath("nextcloud", nextcloud_zip.name).is_file()


def test_import_nextcloud_directory(api_client: TestClient, api_routes: AppRoutes, nextcloud_zip, admin_token):
    selection = nextcloud_zip.name
    import_url = api_routes.migrations_import_type_file_name_import("nextcloud", selection)
    response = api_client.post(import_url, headers=admin_token)

    assert response.status_code == 200

    reports = json.loads(response.content)
    for report in reports:
        assert report.get("status") is True


def test_delete__nextcloud_migration_data(
    api_client: TestClient, api_routes: AppRoutes, nextcloud_zip: Path, admin_token
):
    selection = nextcloud_zip.name
    delete_url = api_routes.migrations_import_type_file_name_delete("nextcloud", selection)
    response = api_client.delete(delete_url, headers=admin_token)

    assert response.status_code == 200
    assert not app_dirs.MIGRATION_DIR.joinpath(nextcloud_zip.name).is_file()


# CSV
@pytest.fixture(scope="session")
def csv_zip():
    zip = TEST_CSV_DIR.joinpath("csv_11.zip")

    zip_copy = TEST_CSV_DIR.joinpath("new_csv_11.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_csv_zip(api_client: TestClient, api_routes: AppRoutes, csv_zip, admin_token):
    upload_url = api_routes.migrations_import_type_upload("csv")
    response = api_client.post(upload_url, files={"archive": csv_zip.open("rb")}, headers=admin_token)

    assert response.status_code == 200

    assert app_dirs.MIGRATION_DIR.joinpath("csv", csv_zip.name).is_file()


def test_import_csv_directory(api_client: TestClient, api_routes: AppRoutes, csv_zip, admin_token):
    selection = csv_zip.name
    import_url = api_routes.migrations_import_type_file_name_import("csv", selection)
    response = api_client.post(import_url, headers=admin_token)

    assert response.status_code == 200

    reports = json.loads(response.content)
    # We provided 11 recipes, one more than the limit, so we expect 10 + 1 reports
    assert len(reports) == 11
    for report in reports[:10]:
        assert report.get("status") is True
    # Last import should hit the limit, resulting in 2 failed imports
    for report in reports[10:]:
        assert report.get("status") is False


def test_delete__csv_migration_data(api_client: TestClient, api_routes: AppRoutes, csv_zip: Path, admin_token):
    selection = csv_zip.name
    delete_url = api_routes.migrations_import_type_file_name_delete("csv", selection)
    response = api_client.delete(delete_url, headers=admin_token)

    assert response.status_code == 200
    assert not app_dirs.MIGRATION_DIR.joinpath(csv_zip.name).is_file()
