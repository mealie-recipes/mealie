import json
from typing import List

import requests
import scrape_schema_recipe
from mealie.core.config import DEBUG_DIR
from fastapi.logger import logger
from mealie.services.image_services import scrape_image
from mealie.schema.recipe import Recipe
from mealie.services.scraper import open_graph
from mealie.services.scraper.cleaner import Cleaner

LAST_JSON = DEBUG_DIR.joinpath("last_recipe.json")


def create_from_url(url: str) -> Recipe:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful.

    Args:
        url (str): a valid string representing a URL

    Returns:
        Recipe: Recipe Object
    """
    r = requests.get(url)
    new_recipe = extract_recipe_from_html(r.text, url)
    print(new_recipe)
    new_recipe = Cleaner.clean(new_recipe, url)
    new_recipe = download_image_for_recipe(new_recipe)

    recipe = Recipe(**new_recipe)

    return recipe


def extract_recipe_from_html(html: str, url: str) -> dict:
    try:
        scraped_recipes: List[dict] = scrape_schema_recipe.loads(html, python_objects=True)
        dump_last_json(scraped_recipes)

        if not scraped_recipes:
            scraped_recipes: List[dict] = scrape_schema_recipe.scrape_url(url, python_objects=True)
    except Exception as e:
        # trying without python_objects
        scraped_recipes: List[dict] = scrape_schema_recipe.loads(html)
        dump_last_json(scraped_recipes)

        if not scraped_recipes:
            scraped_recipes: List[dict] = scrape_schema_recipe.scrape_url(url)

    if scraped_recipes:
        new_recipe: dict = scraped_recipes[0]
        logger.info(f"Recipe Scraped From Web: {new_recipe}")

        if not new_recipe:
            return "fail"  # TODO: Return Better Error Here

        new_recipe = Cleaner.clean(new_recipe, url)
    else:
        new_recipe = open_graph.basic_recipe_from_opengraph(html, url)
        logger.info(f"Recipe Scraped from opengraph metadata: {new_recipe}")

    return new_recipe


def download_image_for_recipe(recipe: dict) -> dict:
    try:
        img_path = scrape_image(recipe.get("image"), recipe.get("slug"))
        recipe["image"] = img_path.name
    except:
        recipe["image"] = "no image"

    return recipe


def dump_last_json(recipe_data: dict):
    with open(LAST_JSON, "w") as f:
        f.write(json.dumps(recipe_data, indent=4, default=str))

    return
