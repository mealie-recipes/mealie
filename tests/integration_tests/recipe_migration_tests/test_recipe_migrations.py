import os
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from mealie.schema.group.group_migration import SupportedMigrations
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.reports.reports import ReportEntryOut
from tests import data as test_data
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_deserialize
from tests.utils.fixture_schemas import TestUser


@dataclass
class MigrationTestData:
    typ: SupportedMigrations
    archive: Path
    search_slug: str

    nutrition_filter: set[str] = field(default_factory=set)
    nutrition_entries: set[str] = field(
        default_factory=lambda: {
            "calories",
            "carbohydrateContent",
            "cholesterolContent",
            "fatContent",
            "fiberContent",
            "proteinContent",
            "saturatedFatContent",
            "sodiumContent",
            "sugarContent",
            "transFatContent",
            "unsaturatedFatContent",
        }
    )


test_cases = [
    MigrationTestData(
        typ=SupportedMigrations.nextcloud,
        archive=test_data.migrations_nextcloud,
        search_slug="skillet-shepherd-s-pie",
        nutrition_filter={
            "transFatContent",
            "unsaturatedFatContent",
        },
    ),
    MigrationTestData(
        typ=SupportedMigrations.paprika,
        archive=test_data.migrations_paprika,
        search_slug="zucchini-kartoffel-frittata",
        nutrition_entries=set(),
    ),
    MigrationTestData(
        typ=SupportedMigrations.chowdown,
        archive=test_data.migrations_chowdown,
        search_slug="roasted-okra",
        nutrition_entries=set(),
    ),
    MigrationTestData(
        typ=SupportedMigrations.copymethat,
        archive=test_data.migrations_copymethat,
        search_slug="spam-zoodles",
        nutrition_entries=set(),
    ),
    MigrationTestData(
        typ=SupportedMigrations.mealie_alpha,
        archive=test_data.migrations_mealie,
        search_slug="old-fashioned-beef-stew",
        nutrition_filter={
            "cholesterolContent",
            "saturatedFatContent",
            "transFatContent",
            "unsaturatedFatContent",
        },
    ),
    MigrationTestData(
        typ=SupportedMigrations.tandoor,
        archive=test_data.migrations_tandoor,
        search_slug="texas-red-chili",
        nutrition_entries=set(),
    ),
    MigrationTestData(
        typ=SupportedMigrations.plantoeat,
        archive=test_data.migrations_plantoeat,
        search_slug="test-recipe",
        nutrition_filter={
            "unsaturatedFatContent",
            "transFatContent",
        },
    ),
    MigrationTestData(
        typ=SupportedMigrations.myrecipebox,
        archive=test_data.migrations_myrecipebox,
        search_slug="beef-cheese-piroshki",
        nutrition_filter={
            "cholesterolContent",
        },
    ),
    MigrationTestData(
        typ=SupportedMigrations.recipekeeper,
        archive=test_data.migrations_recipekeeper,
        search_slug="zucchini-bread",
        nutrition_entries=set(),
    ),
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
def test_recipe_migration(api_client: TestClient, unique_user_fn_scoped: TestUser, mig: MigrationTestData) -> None:
    unique_user = unique_user_fn_scoped
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

    # Validate recipe content
    response = api_client.get(api_routes.recipes_slug(mig.search_slug), headers=unique_user.token)
    recipe = Recipe(**assert_deserialize(response))

    if mig.nutrition_entries:
        assert recipe.nutrition is not None
        nutrition = recipe.nutrition.model_dump(by_alias=True)

        for k in mig.nutrition_entries.difference(mig.nutrition_filter):
            assert k in nutrition and nutrition[k] is not None

    # TODO: validate other types of content


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
            raise Exception(os.listdir(tmpdir))  # noqa: B904

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
