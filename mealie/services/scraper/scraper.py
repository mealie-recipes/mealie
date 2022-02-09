from enum import Enum
from uuid import uuid4

from fastapi import HTTPException, status
from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import Recipe
from mealie.services.recipe.recipe_data_service import RecipeDataService

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
    new_recipe.id = uuid4()

    if not new_recipe:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    logger = get_logger()
    logger.info(f"Image {new_recipe.image}")

    recipe_data_service = RecipeDataService(new_recipe.id)

    try:
        recipe_data_service.scrape_image(new_recipe.image)
        new_recipe.name = slugify(new_recipe.name)
        new_recipe.image = "original.webp"
    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        new_recipe.image = "no image"

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = "No Recipe Name Found - " + str(uuid4())
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe
