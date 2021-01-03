import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from db.recipe_models import RecipeDocument
from jinja2 import Template
from utils.logger import logger

from services.recipe_services import IMG_DIR

CWD = Path(__file__).parent
BACKUP_DIR = CWD.parent.joinpath("data", "backups")
TEMPLATE_DIR = CWD.parent.joinpath("data", "templates")
TEMP_DIR = CWD.parent.joinpath("data", "temp")


def auto_backup_job():
    for backup in BACKUP_DIR.glob("Auto*.zip"):
        backup.unlink()

    templates = []
    for template in TEMPLATE_DIR.iterdir():
        templates.append(template)

    export_db(tag="Auto", templates=templates)
    logger.info("Auto Backup Called")


def import_from_archive(file_name: str) -> list:
    successful_imports = []

    file_path = BACKUP_DIR.joinpath(file_name)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    recipe_dir = TEMP_DIR.joinpath("recipes")
    for recipe in recipe_dir.glob("*.json"):
        with open(recipe, "r") as f:
            recipe_dict = json.loads(f.read())
            del recipe_dict["_id"]
            del recipe_dict["dateAdded"]

            recipeDoc = RecipeDocument(**recipe_dict)
            try:
                recipeDoc.save()
                successful_imports.append(recipe.stem)

            except:
                print("Failed Import:", recipe.stem)

    image_dir = TEMP_DIR.joinpath("images")
    for image in image_dir.iterdir():
        if image.stem in successful_imports:
            shutil.copy(image, IMG_DIR)

    shutil.rmtree(TEMP_DIR)
    return successful_imports


def export_db(tag=None, templates=None):
    if tag:
        export_tag = tag + "_" + datetime.now().strftime("%Y-%b-%d")
    else:
        export_tag = datetime.now().strftime("%Y-%b-%d")

    backup_folder = TEMP_DIR.joinpath(export_tag)
    backup_folder.mkdir(parents=True, exist_ok=True)

    img_folder = backup_folder.joinpath("images")
    img_folder.mkdir(parents=True, exist_ok=True)

    recipe_folder = backup_folder.joinpath("recipes")
    recipe_folder.mkdir(parents=True, exist_ok=True)

    export_images(img_folder)

    if type(templates) == list:
        for template in templates:
            export_recipes(recipe_folder, template)
    elif type(templates) == str:
        export_recipes(recipe_folder, templates)

    zip_path = BACKUP_DIR.joinpath(f"{export_tag}")
    shutil.make_archive(zip_path, "zip", backup_folder)

    shutil.rmtree(backup_folder)
    shutil.rmtree(TEMP_DIR)



def export_images(dest_dir) -> Path:
    for file in IMG_DIR.iterdir():
        shutil.copy(file, dest_dir.joinpath(file.name))


def export_recipes(dest_dir: Path, template=None) -> Path:
    all_recipes = RecipeDocument.objects()
    for recipe in all_recipes:
        json_recipe = recipe.to_json(indent=4)

        if template:
            md_dest = dest_dir.parent.joinpath("templates")
            md_dest.mkdir(parents=True, exist_ok=True)
            template = TEMPLATE_DIR.joinpath(template)
            export_markdown(md_dest, json_recipe, template)

        filename = recipe.slug + ".json"
        file_path = dest_dir.joinpath(filename)

        with open(file_path, "w") as f:
            f.write(json_recipe)


def export_markdown(dest_dir: Path, recipe_data: json, template=Path) -> Path:
    recipe_data: dict = json.loads(recipe_data)
    recipe_template = TEMPLATE_DIR.joinpath("recipes.md")

    with open(recipe_template, "r") as f:
        template = Template(f.read())

    out_file = dest_dir.joinpath(recipe_data["slug"] + ".md")

    content = template.render(recipe=recipe_data)

    with open(out_file, "w") as f:
        f.write(content)


if __name__ == "__main__":
    pass
