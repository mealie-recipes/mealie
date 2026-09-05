"""backfill recipe image column from disk

Revision ID: 4b91d3a7c0e2
Revises: 69e942bab3aa
Create Date: 2026-09-03 16:12:44.183921

`recipes.image` is a cache key, but the frontend now reads its presence as the answer to
"does this recipe have a picture?". That made rows which had drifted out of sync with the
files on disk suddenly visible: a recipe with an image but no key renders the placeholder
and never requests the file, and a recipe with a key but no image asks the media route for
a 404 on every render. This reconciles the column with what is actually on disk, once.

"""

from pathlib import Path

from sqlalchemy import orm, text

from alembic import op
from mealie.core.config import get_app_dirs
from mealie.core.root_logger import get_logger
from mealie.pkgs import cache


# revision identifiers, used by Alembic.
revision = "4b91d3a7c0e2"
down_revision: str | None = "69e942bab3aa"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

NO_IMAGE = "no image"
"""Legacy placeholder the scraper wrote when it had no image. Truthy, so it reads as "has one"."""


def _image_on_disk(recipe_data_dir: Path, recipe_id: str) -> bool:
    # Mirrors Recipe.image_dir_from_id, which can't be used here because it creates the
    # directories it looks in. original.webp is the one file the minifier always writes.
    return recipe_data_dir.joinpath(recipe_id, "images", "original.webp").is_file()


def upgrade() -> None:
    logger = get_logger()
    recipe_data_dir = get_app_dirs().RECIPE_DATA_DIR

    session = orm.Session(bind=op.get_bind())

    rows = session.execute(text("SELECT id, image FROM recipes")).fetchall()
    on_disk = {str(row[0]): _image_on_disk(recipe_data_dir, str(row[0])) for row in rows}

    # An unmounted or misconfigured data volume is indistinguishable from "no recipe has an
    # image", and clearing on that reading would drop every reference in the database. The
    # repairing half is safe either way, so only the clearing half is held back.
    claiming_image = [row for row in rows if row[1] and row[1] != NO_IMAGE]
    skip_clearing = bool(claiming_image) and not any(on_disk.values())
    if skip_clearing:
        logger.warning(
            "Skipping the clearing half of the recipe image backfill: %s recipes reference an image "
            "but no image files were found under %s. If the recipe data volume was not mounted, "
            "nothing was cleared.",
            len(claiming_image),
            recipe_data_dir,
        )

    restored = cleared = 0
    for recipe_id, image in rows:
        has_image = on_disk[str(recipe_id)]

        if has_image and (not image or image == NO_IMAGE):
            session.execute(
                text("UPDATE recipes SET image = :image WHERE id = :id"),
                {"image": cache.new_key(4), "id": recipe_id},
            )
            restored += 1

        elif not has_image and image and not skip_clearing:
            session.execute(text("UPDATE recipes SET image = NULL WHERE id = :id"), {"id": recipe_id})
            cleared += 1

    session.commit()
    logger.info(
        "Recipe image backfill checked %s recipes: %s image references restored, %s cleared",
        len(rows),
        restored,
        cleared,
    )


def downgrade() -> None:
    # The old values were cache keys carrying no meaning beyond "set" or "unset", and every
    # row this touched was one that disagreed with the disk. There is nothing to restore.
    pass
