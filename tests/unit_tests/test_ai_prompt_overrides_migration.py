import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from mealie.services.openai import OpenAIService
from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*a91720b8a7e7*.py"))
    return import_file("add_ai_prompt_overrides", path)


def _upgrade(connection: sa.Connection, settings_ids: list[str]) -> list[sa.Row]:
    connection.execute(sa.text("CREATE TABLE ai_provider_settings (id CHAR(32) PRIMARY KEY)"))
    for settings_id in settings_ids:
        connection.execute(sa.text("INSERT INTO ai_provider_settings (id) VALUES (:id)"), {"id": settings_id})

    with Operations.context(MigrationContext.configure(connection)):
        _migration().upgrade()

    return list(
        connection.execute(
            sa.text("SELECT settings_id, name, mode, content, base_prompt_hash FROM ai_prompt_overrides")
        )
    )


def test_migration_imports_custom_prompt_files_into_every_group(tmp_path, monkeypatch) -> None:
    files = {
        "recipes/build-recipe.txt": "custom build",
        "recipes/compile-source.txt": "custom compile",  # moved to system.compile-source
        "recipes/translate-recipe.txt": "   ",  # blank files fell back to the default
        "recipes/scrape-recipe.txt": "removed prompt",
        "general/debug.txt": "no longer customizable",
    }
    for relative_path, content in files.items():
        (tmp_path / relative_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative_path).write_text(content)
    monkeypatch.setenv("OPENAI_CUSTOM_PROMPT_DIR", str(tmp_path))

    engine = sa.create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            rows = _upgrade(connection, ["a" * 32, "b" * 32])
    finally:
        engine.dispose()

    assert sorted((row.settings_id, row.name, row.mode, row.content) for row in rows) == [
        ("a" * 32, "recipes.build-recipe", "override", "custom build"),
        ("a" * 32, "system.compile-source", "override", "custom compile"),
        ("b" * 32, "recipes.build-recipe", "override", "custom build"),
        ("b" * 32, "system.compile-source", "override", "custom compile"),
    ]

    # Hashed the same way the service hashes it, so the override isn't flagged as outdated right away
    for row in rows:
        assert row.base_prompt_hash == OpenAIService._hash_prompt(OpenAIService.get_default_prompt(row.name))


def test_migration_without_custom_prompt_dir(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_CUSTOM_PROMPT_DIR", raising=False)

    engine = sa.create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            assert _upgrade(connection, ["a" * 32]) == []
    finally:
        engine.dispose()
