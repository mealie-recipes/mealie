import json
from enum import Enum
from typing import Any, Callable

import requests
from fastapi import HTTPException, status
from mealie.core.config import app_dirs
from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe, RecipeStep
from mealie.services.image.image import scrape_image
from mealie.services.scraper import cleaner, open_graph
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, WebsiteNotImplementedError, scrape_me

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
    new_recipe = scrape_from_url(url)
    logger.info(f"Image {new_recipe.image}")
    new_recipe.image = download_image_for_recipe(new_recipe.slug, new_recipe.image)

    return new_recipe


class ParserErrors(str, Enum):
    bad_recipe = "BAD_RECIPE_DATA"
    no_recipe_data = "NO_RECIPE_DATA"
    connection_error = "CONNECTION_ERROR"


def extract_open_graph_values(url) -> Recipe:
    r = requests.get(url)
    recipe = open_graph.basic_recipe_from_opengraph(r.text, url)

    return Recipe(**recipe)


def scrape_from_url(url: str) -> Recipe:
    """Entry function to generating are recipe obejct from a url
    This will determine if a url can be parsed and raise an appropriate error keyword
    This keyword is used on the frontend to reference a localized string to present on the UI.

    Args:
        url (str): String Representing the URL

    Raises:
        HTTPException: 400_BAD_REQUEST - See ParserErrors Class for Key Details

    Returns:
        Recipe: Recipe Model
    """
    try:
        scraped_schema = scrape_me(url)
    except (WebsiteNotImplementedError, AttributeError):
        try:
            scraped_schema = scrape_me(url, wild_mode=True)
        except (NoSchemaFoundInWildMode, AttributeError):
            recipe = extract_open_graph_values(url)
            if recipe.name != "":
                return recipe
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.bad_recipe.value})

    except ConnectionError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.connection_error.value})

    try:
        instruct = scraped_schema.instructions()
    except Exception:
        instruct = []

    try:
        ing = scraped_schema.ingredients()
    except Exception:
        ing = []

    if not instruct and not ing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.no_recipe_data.value})
    else:
        return clean_scraper(scraped_schema, url)


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

    return Recipe(
        name=try_get_default(scraped_data.title, "name", "No Name Found", cleaner.clean_string),
        slug="",
        image=try_get_default(scraped_data.image, "image", None),
        description=try_get_default(None, "description", "", cleaner.clean_string),
        recipe_yield=try_get_default(scraped_data.yields, "recipeYield", "1", cleaner.clean_string),
        recipe_ingredient=try_get_default(scraped_data.ingredients, "recipeIngredient", [""], cleaner.ingredient),
        recipe_instructions=get_instructions(),
        total_time=try_get_default(None, "totalTime", None, cleaner.clean_time),
        prep_time=try_get_default(None, "prepTime", None, cleaner.clean_time),
        perform_time=try_get_default(None, "performTime", None, cleaner.clean_time),
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
