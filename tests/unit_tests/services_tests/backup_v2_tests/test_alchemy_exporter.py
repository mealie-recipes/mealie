import json

from mealie.core.config import get_app_settings
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter


def test_alchemy_exporter():
    settings = get_app_settings()
    exporter = AlchemyExporter(settings.DB_URL)
    data = exporter.dump()

    assert data["alembic_version"] == [{"version_num": "6b0f5f32d602"}]
    assert json.dumps(data, indent=4)  # Make sure data is json-serializable


def test_validate_schemas():
    schema = {
        "alembic_version": [{"version_num": "6b0f5f32d602"}],
    }
    match = {
        "alembic_version": [{"version_num": "6b0f5f32d602"}],
    }

    invalid_version = {
        "alembic_version": [{"version_num": "not-valid-schema"}],
    }

    assert AlchemyExporter.validate_schemas(schema, match)
    assert not AlchemyExporter.validate_schemas(schema, invalid_version)

    schema_with_tables = {
        "alembic_version": [{"version_num": "6b0f5f32d602"}],
        "recipes": [
            {
                "id": 1,
            }
        ],
    }
    match_with_tables = {
        "alembic_version": [{"version_num": "6b0f5f32d602"}],
        "recipes": [
            {
                "id": 2,
            }
        ],
    }

    assert AlchemyExporter.validate_schemas(schema_with_tables, match_with_tables)
