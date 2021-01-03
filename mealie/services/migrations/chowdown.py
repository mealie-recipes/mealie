import shutil
from pathlib import Path

import git
import yaml
from services.image_services import IMG_DIR
from services.recipe_services import Recipe

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

TEMP_DIR = Path(__file__).parent.parent.parent.joinpath("temp")


def pull_repo(repo):
    dest_dir = TEMP_DIR.joinpath("/migration/git_pull")
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    git.Git(dest_dir).clone(repo)

    repo_name = repo.split("/")[-1]
    recipe_dir = dest_dir.joinpath(repo_name, "_recipes")
    image_dir = dest_dir.joinpath(repo_name, "images")

    return recipe_dir, image_dir


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
                print(item)
                if x == 0:
                    recipe_data = item

                elif x == 1:
                    recipe_description = str(item)

        except yaml.YAMLError as exc:
            print(exc)
            return

        reformat_data = {
            "name": recipe_data.get("title"),
            "description": recipe_description,
            "image": recipe_data.get("image", ""),
            "recipeIngredient": recipe_data.get("ingredients"),
            "recipeInstructions": recipe_data.get("directions"),
            "tags": recipe_data.get("tags").split(","),
        }

        new_recipe = Recipe(**reformat_data)

        reformated_list = []
        for instruction in new_recipe.recipeInstructions:
            reformated_list.append({"text": instruction})

        new_recipe.recipeInstructions = reformated_list

        return new_recipe


def chowdown_migrate(repo):
    recipe_dir, image_dir = pull_repo(repo)

    failed_images = []
    for image in image_dir.iterdir():
        try:
            shutil.copy(image, IMG_DIR.joinpath(image.name))
        except:
            failed_images.append(image.name)

    failed_recipes = []
    for recipe in recipe_dir.glob("*.md"):
        print(recipe.name)
        try:
            new_recipe = read_chowdown_file(recipe)
            new_recipe.save_to_db()

        except:
            failed_recipes.append(recipe.name)

    report = {"failedImages": failed_images, "failedRecipes": failed_recipes}

    return report
