from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mealie.schema.group.group_migration import SupportedMigrations
from tests import data as test_data
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_derserialize
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
]

test_ids = [
    "nextcloud_archive",
    "paprika_archive",
    "chowdown_archive",
    "copymethat_archive",
    "mealie_alpha_archive",
    "tandoor_archive",
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
        api_routes.groups_migrations, data=payload, files=file_payload, headers=unique_user.token
    )

    assert response.status_code == 200

    report_id = response.json()["id"]

    # Validate Results
    response = api_client.get(api_routes.groups_reports_item_id(report_id), headers=unique_user.token)

    assert response.status_code == 200

    for item in response.json()["entries"]:
        assert item["success"]

    # Validate Create Event
    params = {"orderBy": "created_at", "orderDirection": "desc"}
    response = api_client.get(api_routes.recipes, params=params, headers=unique_user.token)
    query_data = assert_derserialize(response)
    assert len(query_data["items"])

    recipe_id = query_data["items"][0]["id"]
    params = {"queryFilter": f"recipe_id={recipe_id}"}

    response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    query_data = assert_derserialize(response)
    events = query_data["items"]
    assert len(events)
