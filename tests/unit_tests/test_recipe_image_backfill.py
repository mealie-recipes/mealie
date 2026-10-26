import uuid
from pathlib import Path

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*4b91d3a7c0e2*.py"))
    return import_file("backfill_recipe_image_column", path)


def test_image_on_disk_finds_every_id_spelling(tmp_path: Path) -> None:
    """The backfill reads recipe ids with raw SQL, which bypasses the GUID type decorator.

    Postgres hands back a UUID, SQLite the undashed CHAR(32) it stores, and the directories
    on disk are named with the dashed form either way. Every spelling has to find the file,
    or the backfill silently restores nothing on whichever database it gets wrong.
    """
    migration = _migration()
    recipe_id = uuid.uuid4()

    image = tmp_path.joinpath(str(recipe_id), "images", "original.webp")
    image.parent.mkdir(parents=True)
    image.touch()

    assert migration._image_on_disk(tmp_path, recipe_id), "postgres returns a UUID"
    assert migration._image_on_disk(tmp_path, str(recipe_id)), "dashed string"
    assert migration._image_on_disk(tmp_path, recipe_id.hex), "sqlite returns CHAR(32)"


def test_image_on_disk_is_false_without_a_file(tmp_path: Path) -> None:
    migration = _migration()
    recipe_id = uuid.uuid4()

    tmp_path.joinpath(str(recipe_id), "images").mkdir(parents=True)

    assert not migration._image_on_disk(tmp_path, recipe_id)
    assert not migration._image_on_disk(tmp_path, recipe_id.hex)
