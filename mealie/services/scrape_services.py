import json
from pathlib import Path

from scrape_schema_recipe import scrape_url
from slugify import slugify
from utils.logger import logger

from services.image_services import scrape_image
from services.recipe_services import Recipe

CWD = Path(__file__).parent
TEMP_FILE = CWD.parent.joinpath("data", "debug", "last_recipe.json")


def normalize_data(recipe_data: dict) -> dict:
    if type(recipe_data["recipeYield"]) == list:
        recipe_data["recipeYield"] = recipe_data["recipeYield"][0]

    return recipe_data


def create_from_url(url: str) -> dict:
    recipe_data = process_recipe_url(url)

    with open(TEMP_FILE, "w") as f:
        f.write(json.dumps(recipe_data, indent=4, default=str))

    recipe_data = normalize_data(recipe_data)
    recipe = Recipe(**recipe_data)

    return recipe.save_to_db()


def process_recipe_url(url: str) -> dict:
    new_recipe: dict = scrape_url(url, python_objects=True)[0]
    logger.info(f"Recipe Scraped From Web: {new_recipe}")

    if not new_recipe:
        return "fail"  # TODO: Return Better Error Here

    slug = slugify(new_recipe["name"])
    mealie_tags = {
        "slug": slug,
        "orgURL": url,
        "categories": [],
        "tags": [],
        "dateAdded": None,
        "notes": [],
        "extras": [],
    }

    new_recipe.update(mealie_tags)

    try:
        img_path = scrape_image(new_recipe.get("image"), slug)
        new_recipe["image"] = img_path.name
    except:
        new_recipe["image"] = None

    return new_recipe
