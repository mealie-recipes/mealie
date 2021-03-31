import json
import logging
import shutil
import zipfile
from pathlib import Path

from mealie.core.config import app_dirs
from mealie.db.database import db
from mealie.schema.recipe import Recipe
from mealie.services.scraper.cleaner import Cleaner


def process_selection(selection: Path) -> Path:
    if selection.is_dir():
        return selection
    elif selection.suffix == ".zip":
        with zipfile.ZipFile(selection, "r") as zip_ref:
            nextcloud_dir = app_dirs.TEMP_DIR.joinpath("nextcloud")
            nextcloud_dir.mkdir(exist_ok=False, parents=True)
            zip_ref.extractall(nextcloud_dir)
        return nextcloud_dir
    else:
        return None


def import_recipes(recipe_dir: Path) -> Recipe:
    image = False
    for file in recipe_dir.glob("full.*"):
        image = file

    for file in recipe_dir.glob("*.json"):
        recipe_file = file

    with open(recipe_file, "r") as f:
        recipe_dict = json.loads(f.read())

    recipe_data = Cleaner.clean(recipe_dict)

    image_name = None
    if image:
        image_name = recipe_data["slug"] + image.suffix
        recipe_data["image"] = image_name
    else:
        recipe_data["image"] = "none"

    recipe = Recipe(**recipe_data)

    if image:
        shutil.copy(image, app_dirs.IMG_DIR.joinpath(image_name))

    return recipe


def prep():
    try:
        shutil.rmtree(app_dirs.TEMP_DIR)
    except:
        pass
    app_dirs.TEMP_DIR.mkdir(exist_ok=True, parents=True)


def cleanup():
    shutil.rmtree(app_dirs.TEMP_DIR)


def migrate(session, selection: str):
    prep()
    app_dirs.MIGRATION_DIR.mkdir(exist_ok=True)
    selection = app_dirs.MIGRATION_DIR.joinpath(selection)

    nextcloud_dir = process_selection(selection)

    successful_imports = []
    failed_imports = []
    for dir in nextcloud_dir.iterdir():
        if dir.is_dir():

            try:
                recipe = import_recipes(dir)
                db.recipes.create(session, recipe.dict())

                successful_imports.append(recipe.name)
            except:
                logging.error(f"Failed Nextcloud Import: {dir.name}")
                logging.exception("")
                failed_imports.append(dir.name)

    cleanup()

    return {"successful": successful_imports, "failed": failed_imports}
