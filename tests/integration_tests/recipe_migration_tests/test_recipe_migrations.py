from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mealie.schema.group.group_migration import SupportedMigrations
from tests import data as test_data
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/migrations"

    def report(item_id: str) -> str:
        return f"/api/groups/reports/{item_id}"


@dataclass
class MigrationTestData:
    typ: SupportedMigrations
    archive: Path


test_cases = [
    MigrationTestData(typ=SupportedMigrations.nextcloud, archive=test_data.migrations_nextcloud),
    MigrationTestData(typ=SupportedMigrations.paprika, archive=test_data.migrations_paprika),
    MigrationTestData(typ=SupportedMigrations.chowdown, archive=test_data.migrations_chowdown),
]


@pytest.mark.parametrize("mig", test_cases)
def test_recipe_migration(api_client: TestClient, unique_user: TestUser, mig: MigrationTestData) -> None:
    payload = {
        "migration_type": mig.typ.value,
    }

    file_payload = {
        "archive": mig.archive.read_bytes(),
    }

    response = api_client.post(Routes.base, data=payload, files=file_payload, headers=unique_user.token)

    assert response.status_code == 200

    report_id = response.json()["id"]

    # Validate Results
    response = api_client.get(Routes.report(report_id), headers=unique_user.token)

    assert response.status_code == 200

    for item in response.json()["entries"]:
        assert item["success"]
