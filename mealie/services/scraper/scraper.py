from __future__ import annotations

from enum import Enum
from uuid import uuid4

from fastapi import HTTPException, status
from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe
from mealie.services.image.image import scrape_image

from .recipe_scraper import RecipeScraper


class ParserErrors(str, Enum):
    BAD_RECIPE_DATA = "BAD_RECIPE_DATA"
    NO_RECIPE_DATA = "NO_RECIPE_DATA"
    CONNECTION_ERROR = "CONNECTION_ERROR"


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

    logger = get_logger()
    logger.info(f"Image {new_recipe.image}")
    new_recipe.image = download_image_for_recipe(new_recipe.slug, new_recipe.image)

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = "No Recipe Found - " + uuid4().hex
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe


def download_image_for_recipe(slug, image_url) -> str | None:
    img_name = None
    try:
        img_path = scrape_image(image_url, slug)
        img_name = img_path.name
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error Scraping Image: {e}")
        img_name = None

    return img_name or "no image"
