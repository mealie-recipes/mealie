import json
import shutil

import pytest
from mealie.core.config import MIGRATION_DIR
from tests.test_config import TEST_CHOWDOWN_DIR, TEST_NEXTCLOUD_DIR
from tests.utils.routes import MIGRATIONS_PREFIX, RECIPES_PREFIX


### Chowdown
@pytest.fixture(scope="session")
def chowdown_zip():
    zip = TEST_CHOWDOWN_DIR.joinpath("test_chowdown-gh-pages.zip")

    zip_copy = TEST_CHOWDOWN_DIR.joinpath("chowdown-gh-pages.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_chowdown_zip(api_client, chowdown_zip):

    response = api_client.post(
        f"{MIGRATIONS_PREFIX}/chowdown/upload",
        files={"archive": chowdown_zip.open("rb")},
    )

    assert response.status_code == 200

    assert MIGRATION_DIR.joinpath("chowdown", chowdown_zip.name).is_file()


def test_import_chowdown_directory(api_client, chowdown_zip):
    selection = chowdown_zip.name
    response = api_client.post(f"{MIGRATIONS_PREFIX}/chowdown/{selection}/import")

    assert response.status_code == 200

    report = json.loads(response.content)
    assert report["failed"] == []

    expected_slug = "roasted-okra"
    response = api_client.get(f"{RECIPES_PREFIX}/{expected_slug}")
    assert response.status_code == 200


def test_delete_chowdown_migration_data(api_client, chowdown_zip):
    selection = chowdown_zip.name
    response = api_client.delete(f"{MIGRATIONS_PREFIX}/chowdown/{selection}/delete")

    assert response.status_code == 200
    assert not MIGRATION_DIR.joinpath(chowdown_zip.name).is_file()


### Nextcloud
@pytest.fixture(scope="session")
def nextcloud_zip():
    zip = TEST_NEXTCLOUD_DIR.joinpath("nextcloud.zip")

    zip_copy = TEST_NEXTCLOUD_DIR.joinpath("new_nextcloud.zip")

    shutil.copy(zip, zip_copy)

    yield zip_copy

    zip_copy.unlink()


def test_upload_nextcloud_zip(api_client, nextcloud_zip):

    response = api_client.post(
        f"{MIGRATIONS_PREFIX}/nextcloud/upload",
        files={"archive": nextcloud_zip.open("rb")},
    )

    assert response.status_code == 200

    assert MIGRATION_DIR.joinpath("nextcloud", nextcloud_zip.name).is_file()


def test_import_nextcloud_directory(api_client, nextcloud_zip):
    selection = nextcloud_zip.name
    response = api_client.post(f"{MIGRATIONS_PREFIX}/nextcloud/{selection}/import")

    assert response.status_code == 200

    report = json.loads(response.content)
    assert report["failed"] == []

    expected_slug = "air-fryer-shrimp"
    response = api_client.get(f"{RECIPES_PREFIX}/{expected_slug}")
    assert response.status_code == 200


def test_delete__nextcloud_migration_data(api_client, nextcloud_zip):
    selection = nextcloud_zip.name
    response = api_client.delete(f"{MIGRATIONS_PREFIX}/nextcloud/{selection}/delete")

    assert response.status_code == 200
    assert not MIGRATION_DIR.joinpath(nextcloud_zip.name).is_file()
