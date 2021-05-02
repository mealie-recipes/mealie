from pathlib import Path

from mealie.core.config import app_dirs
from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe

logger = get_logger()


def check_asset(original_slug, recipe: Recipe) -> Path:
    if original_slug == recipe.slug:
        return recipe.assets

    current_dir = app_dirs.RECIPE_DATA_DIR.joinpath(original_slug)

    try:
        current_dir.rename(recipe.directory)
    except FileNotFoundError:
        logger.error(f"Recipe Directory not Found: {original_slug}")
    logger.info(f"Renaming Recipe Directory: {original_slug} -> {recipe.slug}")

    return current_dir.absolute()
