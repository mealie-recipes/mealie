import json

from mealie.core.config import get_app_settings
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from tests.utils.alembic_reader import alembic_versions


def test_alchemy_exporter():
    settings = get_app_settings()
    exporter = AlchemyExporter(settings.DB_URL)
    data = exporter.dump()

    assert data["alembic_version"] == alembic_versions()
    assert json.dumps(data, indent=4)  # Make sure data is json-serializable


def test_validate_schemas():
    schema = {
        "alembic_version": alembic_versions(),
    }
    match = {
        "alembic_version": alembic_versions(),
    }

    invalid_version = {
        "alembic_version": [{"version_num": "not-valid-schema"}],
    }

    assert AlchemyExporter.validate_schemas(schema, match)
    assert not AlchemyExporter.validate_schemas(schema, invalid_version)

    schema_with_tables = {
        "alembic_version": alembic_versions(),
        "recipes": [
            {
                "id": 1,
            }
        ],
    }
    match_with_tables = {
        "alembic_version": alembic_versions(),
        "recipes": [
            {
                "id": 2,
            }
        ],
    }

    assert AlchemyExporter.validate_schemas(schema_with_tables, match_with_tables)
    assert AlchemyExporter.validate_schemas(schema_with_tables, match_with_tables)
    assert AlchemyExporter.validate_schemas(schema_with_tables, match_with_tables)
