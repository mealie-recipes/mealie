import json
import logging
import shutil
import zipfile
from pathlib import Path

from app_config import IMG_DIR, MIGRATION_DIR, TEMP_DIR
from services.recipe_services import Recipe
from services.scrape_services import normalize_data, process_recipe_data


def process_selection(selection: Path) -> Path:
    if selection.is_dir():
        return selection
    elif selection.suffix == ".zip":
        with zipfile.ZipFile(selection, "r") as zip_ref:
            nextcloud_dir = TEMP_DIR.joinpath("nextcloud")
            nextcloud_dir.mkdir(exist_ok=False, parents=True)
            zip_ref.extractall(nextcloud_dir)
        return nextcloud_dir
    else:
        return None


def import_recipes(recipe_dir: Path) -> Recipe:
    image = False
    for file in recipe_dir.glob("full.*"):
        image = file

    recipe_file = recipe_dir.joinpath("recipe.json")

    with open(recipe_file, "r") as f:
        recipe_dict = json.loads(f.read())

    recipe_dict = process_recipe_data(recipe_dict)
    recipe_data = normalize_data(recipe_dict)

    image_name = None
    if image:
        image_name = recipe_data["slug"] + image.suffix
        recipe_data["image"] = image_name
    else:
        recipe_data["image"] = "none"

    recipe = Recipe(**recipe_data)

    if image:
        shutil.copy(image, IMG_DIR.joinpath(image_name))

    return recipe


def prep():
    try:
        shutil.rmtree(TEMP_DIR)
    except:
        pass
    TEMP_DIR.mkdir(exist_ok=True, parents=True)


def cleanup():
    shutil.rmtree(TEMP_DIR)


def migrate(session, selection: str):
    prep()
    MIGRATION_DIR.mkdir(exist_ok=True)
    selection = MIGRATION_DIR.joinpath(selection)

    nextcloud_dir = process_selection(selection)

    successful_imports = []
    failed_imports = []
    for dir in nextcloud_dir.iterdir():
        if dir.is_dir():

            try:
                recipe = import_recipes(dir)
                recipe.save_to_db(session)
                successful_imports.append(recipe.name)
            except:
                logging.error(f"Failed Nextcloud Import: {dir.name}")
                failed_imports.append(dir.name)

    cleanup()

    return {"successful": successful_imports, "failed": failed_imports}
