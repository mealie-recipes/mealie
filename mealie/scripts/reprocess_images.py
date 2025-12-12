import sqlalchemy as sa
from PIL import Image
from pydantic import UUID4

from mealie.core import root_logger
from mealie.db.db_setup import session_context
from mealie.db.models.recipe import RecipeModel
from mealie.services.recipe.recipe_data_service import RecipeDataService

logger = root_logger.get_logger()


def check_needs_reprocess(recipe_id: UUID4) -> bool:
    """
    Check if a recipe's images need reprocessing by examining tiny image dimensions.
    New processing creates 600x600 tiny images, old processing created 300x300.

    Returns True if needs reprocessing (has old 300x300 tiny image or missing images).
    """

    try:
        service = RecipeDataService(recipe_id)
        tiny_path = service.dir_image / "tiny-original.webp"
        original_path = service.dir_image / "original.webp"

        if not original_path.exists():
            return False  # Cannot reprocess without original image

        if not tiny_path.exists():
            return True  # Needs reprocessing if tiny image is missing

    except Exception:
        logger.error(f"Failed to access recipe {recipe_id} images for reprocessing check; skipping")
        return False

    try:
        with Image.open(tiny_path) as img:
            # This will miss images which were originally smaller than 300x300,
            # but we probably don't care about those anyway
            return img.width == 300 and img.height == 300
    except Exception:
        logger.error(f"Failed to open tiny image for recipe {recipe_id}; assuming reprocessing needed")
        return False


def fetch_recipe_ids(force_process_all=False) -> set[UUID4]:
    logger.info("Fetching recipes for image reprocessing")
    if force_process_all:
        logger.info("!!Force processing all recipes regardless of current image state")

    with session_context() as session:
        result = session.execute(sa.text(f"SELECT id FROM {RecipeModel.__tablename__}"))

    recipe_ids = {UUID4(row[0]) for row in result}
    if force_process_all:
        return recipe_ids

    else:
        return {recipe_id for recipe_id in recipe_ids if check_needs_reprocess(recipe_id)}


def reprocess_recipe_images(recipe_id: UUID4) -> None:
    pass  # TODO


def main() -> None:
    recipe_ids = fetch_recipe_ids(force_process_all=False)
    if not recipe_ids:
        logger.info("No recipes need image reprocessing. Exiting...")
        exit(0)

    confirmed = input(
        f"Found {len(recipe_ids)} {'recipe' if len(recipe_ids) == 1 else 'recipes'} "
        "needing image reprocessing. Proceed? (y/n) "
    )
    if confirmed.lower() != "y":
        print("aborting")  # noqa
        exit(0)

    failed_recipe_ids: set[UUID4] = set()
    for i, recipe_id in enumerate(recipe_ids, start=1):
        try:
            reprocess_recipe_images(recipe_id)
        except Exception:
            logger.exception(f"Failed to reprocess images for recipe {recipe_id}")
            failed_recipe_ids.add(recipe_id)

        progress_freq = 20 if len(recipe_ids) <= 1000 else 100
        if not i % progress_freq:
            perc = (i / len(recipe_ids)) * 100
            logger.info(f"{perc:.2f}% complete ({i}/{len(recipe_ids)})")

    logger.info(f"Image reprocessing complete. {len(recipe_ids) - len(failed_recipe_ids)} successfully processed")
    if failed_recipe_ids:
        logger.error(f"Failed recipes: {', '.join(str(rid) for rid in failed_recipe_ids)}")

    exit(0)


if __name__ == "__main__":
    main()
