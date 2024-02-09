from enum import Enum
from uuid import uuid4

from fastapi import HTTPException, status
from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import cache
from mealie.schema.recipe import Recipe
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraped_extras import ScrapedExtras

from .recipe_scraper import RecipeScraper


class ParserErrors(str, Enum):
    BAD_RECIPE_DATA = "BAD_RECIPE_DATA"
    NO_RECIPE_DATA = "NO_RECIPE_DATA"
    CONNECTION_ERROR = "CONNECTION_ERROR"


async def create_from_url(url: str, translator: Translator) -> tuple[Recipe, ScrapedExtras | None]:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful.

    Args:
        url (str): a valid string representing a URL

    Returns:
        Recipe: Recipe Object
    """
    scraper = RecipeScraper(translator)
    new_recipe, extras = await scraper.scrape(url)

    if not new_recipe:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    new_recipe.id = uuid4()
    logger = get_logger()
    logger.debug(f"Image {new_recipe.image}")

    recipe_data_service = RecipeDataService(new_recipe.id)

    try:
        await recipe_data_service.scrape_image(new_recipe.image)

        if new_recipe.name is None:
            new_recipe.name = "Untitled"

        new_recipe.slug = slugify(new_recipe.name)
        new_recipe.image = cache.new_key(4)
    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        new_recipe.image = "no image"

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = f"No Recipe Name Found - {str(uuid4())}"
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe, extras
