from __future__ import annotations

from enum import Enum
from uuid import uuid4

from fastapi import HTTPException, status
from recipe_scrapers import NoSchemaFoundInWildMode, WebsiteNotImplementedError, scrape_me
from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe
from mealie.services.image.image import scrape_image

from .recipe_scraper import RecipeScraper

logger = get_logger()


def create_from_url(url: str) -> Recipe:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful.

    Args:
        url (str): a valid string representing a URL

    Returns:
        Recipe: Recipe Object
    """
    scraper = RecipeScraper()
    new_recipe = scraper.scrape(url)

    if not new_recipe:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    logger.info(f"Image {new_recipe.image}")
    new_recipe.image = download_image_for_recipe(new_recipe.slug, new_recipe.image)

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = "No Recipe Found - " + uuid4().hex
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe


class ParserErrors(str, Enum):
    BAD_RECIPE_DATA = "BAD_RECIPE_DATA"
    NO_RECIPE_DATA = "NO_RECIPE_DATA"
    CONNECTION_ERROR = "CONNECTION_ERROR"


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
            logger.error("Recipe Scraper was unable to extract a recipe.")
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


def download_image_for_recipe(slug, image_url) -> str | None:
    img_name = None
    try:
        img_path = scrape_image(image_url, slug)
        img_name = img_path.name
    except Exception as e:
        logger.error(f"Error Scraping Image: {e}")
        img_name = None

    return img_name or "no image"
