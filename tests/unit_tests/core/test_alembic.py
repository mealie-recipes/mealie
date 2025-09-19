import pathlib

from pydantic import BaseModel

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


class AlembicMigration(BaseModel):
    path: pathlib.Path
    revision: str | None = None
    down_revision: str | None = None


def test_alembic_revisions_are_in_order() -> None:
    # read all files
    paths = sorted(ALEMBIC_MIGRATIONS.glob("*.py"))

    # convert to sorted list of AlembicMigration
    migrations: list[AlembicMigration] = []

    for path in paths:
        mod = import_file("alembic_version", path)

        revision = getattr(mod, "revision", None)
        down_revision = getattr(mod, "down_revision", None)

        migrations.append(
            AlembicMigration(
                path=path,
                revision=revision,
                down_revision=down_revision,
            )
        )

    # step through each migration and check
    #   - revision is in order
    #   - down_revision is in order
    #   - down_revision is the previous revision
    last = None
    for migration in migrations:
        if last is not None:
            assert last.revision == migration.down_revision, (
                f"{last.revision} != {migration.down_revision} for {migration.path}"
            )

        last = migration
        last = migration
