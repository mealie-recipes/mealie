from pathlib import Path
from shutil import copytree, rmtree

from mealie.core.config import app_dirs
from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe

logger = get_logger()


def check_assets(original_slug, recipe: Recipe) -> None:
    if original_slug != recipe.slug:
        current_dir = app_dirs.RECIPE_DATA_DIR.joinpath(original_slug)

        try:
            copytree(current_dir, recipe.directory, dirs_exist_ok=True)

        except FileNotFoundError:
            logger.error(f"Recipe Directory not Found: {original_slug}")
        logger.info(f"Renaming Recipe Directory: {original_slug} -> {recipe.slug}")

    all_asset_files = [x.file_name for x in recipe.assets]
    for file in recipe.asset_dir.iterdir():
        file: Path
        if file.is_dir():
            continue
        if file.name not in all_asset_files:
            file.unlink()


def delete_assets(recipe_slug):
    recipe_dir = Recipe(slug=recipe_slug).directory
    rmtree(recipe_dir, ignore_errors=True)
    logger.info(f"Recipe Directory Removed: {recipe_slug}")
