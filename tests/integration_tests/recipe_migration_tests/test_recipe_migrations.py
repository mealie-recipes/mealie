import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from mealie.schema.group.group_migration import SupportedMigrations
from mealie.schema.reports.reports import ReportEntryOut
from tests import data as test_data
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_deserialize
from tests.utils.fixture_schemas import TestUser


@dataclass
class MigrationTestData:
    typ: SupportedMigrations
    archive: Path


test_cases = [
    MigrationTestData(typ=SupportedMigrations.nextcloud, archive=test_data.migrations_nextcloud),
    MigrationTestData(typ=SupportedMigrations.paprika, archive=test_data.migrations_paprika),
    MigrationTestData(typ=SupportedMigrations.chowdown, archive=test_data.migrations_chowdown),
    MigrationTestData(typ=SupportedMigrations.copymethat, archive=test_data.migrations_copymethat),
    MigrationTestData(typ=SupportedMigrations.mealie_alpha, archive=test_data.migrations_mealie),
    MigrationTestData(typ=SupportedMigrations.tandoor, archive=test_data.migrations_tandoor),
    MigrationTestData(typ=SupportedMigrations.plantoeat, archive=test_data.migrations_plantoeat),
    MigrationTestData(typ=SupportedMigrations.myrecipebox, archive=test_data.migrations_myrecipebox),
    MigrationTestData(typ=SupportedMigrations.recipekeeper, archive=test_data.migrations_recipekeeper),
]

test_ids = [
    "nextcloud_archive",
    "paprika_archive",
    "chowdown_archive",
    "copymethat_archive",
    "mealie_alpha_archive",
    "tandoor_archive",
    "plantoeat_archive",
    "myrecipebox_csv",
    "recipekeeper_archive",
]


@pytest.mark.parametrize("mig", test_cases, ids=test_ids)
def test_recipe_migration(api_client: TestClient, unique_user: TestUser, mig: MigrationTestData) -> None:
    payload = {
        "migration_type": mig.typ.value,
    }

    file_payload = {
        "archive": mig.archive.read_bytes(),
    }

    response = api_client.post(
        api_routes.groups_migrations,
        data=payload,
        files=file_payload,
        headers=unique_user.token,
    )

    assert response.status_code == 200

    report_id = response.json()["id"]

    # Validate Results
    response = api_client.get(api_routes.groups_reports_item_id(report_id), headers=unique_user.token)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["entries"]

    for item in response_json["entries"]:
        assert item["success"]

    # Validate Create Event
    params = {"orderBy": "created_at", "orderDirection": "desc"}
    response = api_client.get(api_routes.recipes, params=params, headers=unique_user.token)
    query_data = assert_deserialize(response)
    assert len(query_data["items"])

    recipe_id = query_data["items"][0]["id"]
    params = {"queryFilter": f"recipe_id={recipe_id}"}

    response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    query_data = assert_deserialize(response)
    events = query_data["items"]
    assert len(events)


def test_bad_mealie_alpha_data_is_ignored(api_client: TestClient, unique_user: TestUser):
    with TemporaryDirectory() as tmpdir:
        with ZipFile(test_data.migrations_mealie) as zf:
            zf.extractall(tmpdir)

        invalid_recipe_dir = os.path.join(tmpdir, "mealie_2021-Dec-08", "recipes", "invalid-recipe")
        os.makedirs(invalid_recipe_dir, exist_ok=True)
        invalid_json_path = os.path.join(invalid_recipe_dir, "invalid-recipe.json")
        try:
            with open(invalid_json_path, "w"):
                pass  # write nothing to the file, which is invalid JSON
        except Exception:
            raise Exception(os.listdir(tmpdir))

        modified_test_data = os.path.join(tmpdir, "modified-test-data.zip")
        with ZipFile(modified_test_data, "w") as zf:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, arcname=os.path.relpath(file_path, tmpdir))

        payload = {
            "migration_type": SupportedMigrations.mealie_alpha.value,
        }

        file_payload = {
            "archive": Path(modified_test_data).read_bytes(),
        }

        response = api_client.post(
            api_routes.groups_migrations,
            data=payload,
            files=file_payload,
            headers=unique_user.token,
        )

        assert response.status_code == 200
        report_id = response.json()["id"]

    # Validate Results
    response = api_client.get(api_routes.groups_reports_item_id(report_id), headers=unique_user.token)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["entries"]

    failed_item = None
    failed_item_count = 0
    for item in response_json["entries"]:
        if item["success"]:
            continue

        failed_item = item
        failed_item_count += 1

    assert failed_item
    assert failed_item_count == 1

    report_entry = ReportEntryOut.model_validate(failed_item)
    assert report_entry.message == "Failed to import invalid-recipe.json"
    assert report_entry.exception == "JSONDecodeError: Expecting value: line 1 column 1 (char 0)"
