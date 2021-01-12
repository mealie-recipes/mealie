import json
import shutil
import zipfile
from pathlib import Path

from db.mongo.recipe_models import RecipeDocument
from utils.logger import logger

from services.recipe_services import IMG_DIR

CWD = Path(__file__).parent
BACKUP_DIR = CWD.parent.joinpath("data", "backups")
TEMPLATE_DIR = CWD.parent.joinpath("data", "templates")
TEMP_DIR = CWD.parent.joinpath("data", "temp")


def import_migration(recipe_dict: dict) -> dict:
    del recipe_dict["_id"]
    del recipe_dict["dateAdded"]

    # Migration from list to Object Type Data
    if type(recipe_dict["extras"]) == list:
        recipe_dict["extras"] = {}

    return recipe_dict


def import_from_archive(file_name: str) -> list:
    successful_imports = []
    failed_imports = []

    file_path = BACKUP_DIR.joinpath(file_name)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    recipe_dir = TEMP_DIR.joinpath("recipes")
    for recipe in recipe_dir.glob("*.json"):
        with open(recipe, "r") as f:
            recipe_dict = json.loads(f.read())

            try:
                recipe_dict = import_migration(recipe_dict)
                recipeDoc = RecipeDocument(**recipe_dict)
                recipeDoc.save()
                successful_imports.append(recipe.stem)
            except:
                logger.info(f"Failed Import: {recipe.stem}")
                failed_imports.append(recipe.stem)

    image_dir = TEMP_DIR.joinpath("images")
    for image in image_dir.iterdir():
        if image.stem in successful_imports:
            shutil.copy(image, IMG_DIR)

    shutil.rmtree(TEMP_DIR)

    return {"successful": successful_imports, "failed": failed_imports}


if __name__ == "__main__":
    pass
