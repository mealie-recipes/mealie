import json
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

import requests
from fastapi import HTTPException, status
from mealie.core.config import app_dirs
from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe, RecipeStep
from mealie.services.image.image import scrape_image
from mealie.services.scraper import cleaner, open_graph
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, WebsiteNotImplementedError, scrape_me
from slugify import slugify

LAST_JSON = app_dirs.DEBUG_DIR.joinpath("last_recipe.json")


logger = get_logger()


def create_from_url(url: str) -> Recipe:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful.

    Args:
        url (str): a valid string representing a URL

    Returns:
        Recipe: Recipe Object
    """
    # Try the different scrapers in order.
    if scraped_data := scrape_from_url(url):
        new_recipe = clean_scraper(scraped_data, url)
    elif og_dict := extract_open_graph_values(url):
        new_recipe = Recipe(**og_dict)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    logger.info(f"Image {new_recipe.image}")
    new_recipe.image = download_image_for_recipe(new_recipe.slug, new_recipe.image)

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = "No Recipe Found" + uuid4().hex
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe


class ParserErrors(str, Enum):
    BAD_RECIPE_DATA = "BAD_RECIPE_DATA"
    NO_RECIPE_DATA = "NO_RECIPE_DATA"
    CONNECTION_ERROR = "CONNECTION_ERROR"


def extract_open_graph_values(url) -> Optional[dict]:
    r = requests.get(url)
    recipe = open_graph.basic_recipe_from_opengraph(r.text, url)
    if recipe.get("name", "") == "":
        return None
    return recipe


def scrape_from_url(url: str):
    """Entry function to scrape a recipe from a url
    This will determine if a url can be parsed and return None if not, to allow another parser to try.
    This keyword is used on the frontend to reference a localized string to present on the UI.

    Args:
        url (str): String Representing the URL

    Raises:
        HTTPException: 400_BAD_REQUEST - See ParserErrors Class for Key Details

    Returns:
        Optional[Scraped schema for cleaning]
    """
    try:
        scraped_schema = scrape_me(url)
    except (WebsiteNotImplementedError, AttributeError):
        try:
            scraped_schema = scrape_me(url, wild_mode=True)
        except (NoSchemaFoundInWildMode, AttributeError):
            # Recipe_scraper was unable to extract a recipe.
            return None

    except ConnectionError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.CONNECTION_ERROR.value})

    # Check to see if the recipe is valid
    try:
        ingredients = scraped_schema.ingredients()
        instruct = scraped_schema.instructions()
    except Exception:
        ingredients = []
        instruct = []

    if instruct and ingredients:
        return scraped_schema

    # recipe_scrapers did not get a valid recipe.
    # Return None to let another scraper try.
    return None


def clean_scraper(scraped_data: SchemaScraperFactory.SchemaScraper, url: str) -> Recipe:
    def try_get_default(func_call: Callable, get_attr: str, default: Any, clean_func=None):
        value = default
        try:
            value = func_call()
        except Exception:
            logger.error(f"Error parsing recipe func_call for '{get_attr}'")

        if value == default:
            try:
                value = scraped_data.schema.data.get(get_attr)
            except Exception:
                logger.error(f"Error parsing recipe attribute '{get_attr}'")

        if clean_func:
            value = clean_func(value)

        return value

    def get_instructions() -> list[dict]:
        instruction_as_text = try_get_default(
            scraped_data.instructions, "recipeInstructions", ["No Instructions Found"]
        )

        logger.info(f"Scraped Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

        instruction_as_text = cleaner.instructions(instruction_as_text)

        logger.info(f"Cleaned Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

        try:
            return [RecipeStep(title="", text=x.get("text")) for x in instruction_as_text]
        except TypeError:
            return []

    cook_time = try_get_default(None, "performTime", None, cleaner.clean_time) or try_get_default(
        None, "cookTime", None, cleaner.clean_time
    )

    return Recipe(
        name=try_get_default(scraped_data.title, "name", "No Name Found", cleaner.clean_string),
        slug="",
        image=try_get_default(None, "image", None),
        description=try_get_default(None, "description", "", cleaner.clean_string),
        nutrition=try_get_default(None, "nutrition", None, cleaner.clean_nutrition),
        recipe_yield=try_get_default(scraped_data.yields, "recipeYield", "1", cleaner.clean_string),
        recipe_ingredient=try_get_default(scraped_data.ingredients, "recipeIngredient", [""], cleaner.ingredient),
        recipe_instructions=get_instructions(),
        total_time=try_get_default(None, "totalTime", None, cleaner.clean_time),
        prep_time=try_get_default(None, "prepTime", None, cleaner.clean_time),
        perform_time=cook_time,
        org_url=url,
    )


def download_image_for_recipe(slug, image_url) -> dict:
    img_name = None
    try:
        img_path = scrape_image(image_url, slug)
        img_name = img_path.name
    except Exception as e:
        logger.error(f"Error Scraping Image: {e}")
        img_name = None

    return img_name or "no image"


def dump_last_json(recipe_data: dict):
    with open(LAST_JSON, "w") as f:
        f.write(json.dumps(recipe_data, indent=4, default=str))

    return
