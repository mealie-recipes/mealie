import shutil
from pathlib import Path

import yaml
from fastapi.logger import logger
from mealie.core.config import IMG_DIR, TEMP_DIR
from mealie.db.database import db
from mealie.schema.recipe import Recipe
from mealie.utils.unzip import unpack_zip
from sqlalchemy.orm.session import Session

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def read_chowdown_file(recipe_file: Path) -> Recipe:
    """Parse through the yaml file to try and pull out the relavent information.
    Some issues occur when ":" are used in the text. I have no put a lot of effort
    into this so there may be better ways of going about it. Currently, I get about 80-90%
    of recipes from repos I've tried.

    Args:
        recipe_file (Path): Path to the .yml file

    Returns:
        Recipe: Recipe class object
    """

    with open(recipe_file, "r") as stream:
        recipe_description: str = str
        recipe_data: dict = {}
        try:
            for x, item in enumerate(yaml.load_all(stream, Loader=Loader)):
                if x == 0:
                    recipe_data = item

                elif x == 1:
                    recipe_description = str(item)

        except yaml.YAMLError:
            return

        reformat_data = {
            "name": recipe_data.get("title"),
            "description": recipe_description,
            "image": recipe_data.get("image", ""),
            "recipeIngredient": recipe_data.get("ingredients"),
            "recipeInstructions": recipe_data.get("directions"),
            "tags": recipe_data.get("tags").split(","),
        }

        reformated_list = [{"text": instruction} for instruction in reformat_data["recipeInstructions"]]

        reformat_data["recipeInstructions"] = reformated_list

        return Recipe(**reformat_data)


def chowdown_migrate(session: Session, zip_file: Path):

    temp_dir = unpack_zip(zip_file)

    with temp_dir as dir:
        chow_dir = next(Path(dir).iterdir())
        image_dir = TEMP_DIR.joinpath(chow_dir, "images")
        recipe_dir = TEMP_DIR.joinpath(chow_dir, "_recipes")

        failed_recipes = []
        successful_recipes = []
        for recipe in recipe_dir.glob("*.md"):
            try:
                new_recipe = read_chowdown_file(recipe)
                db.recipes.create(session, new_recipe.dict())
                successful_recipes.append(new_recipe.name)
            except Exception as inst:
                session.rollback()
                logger.error(inst)
                failed_recipes.append(recipe.stem)

        failed_images = []
        for image in image_dir.iterdir():
            try:
                if image.stem not in failed_recipes:
                    shutil.copy(image, IMG_DIR.joinpath(image.name))
            except Exception as inst:
                logger.error(inst)
                failed_images.append(image.name)
        report = {"successful": successful_recipes, "failed": failed_recipes}

    return report
