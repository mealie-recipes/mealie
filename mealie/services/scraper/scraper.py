from enum import Enum
from re import search as regex_search
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


async def create_from_html(
    url: str, translator: Translator, html: str | None = None
) -> tuple[Recipe, ScrapedExtras | None]:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful. Optionally pass in the HTML to skip fetching it.

    Args:
        url (str): a valid string representing a URL
        html (str | None): optional HTML string to skip network request. Defaults to None.

    Returns:
        Recipe: Recipe Object
    """
    scraper = RecipeScraper(translator)

    if not html:
        extracted_url = regex_search(r"(https?://|www\.)[^\s]+", url)
        if not extracted_url:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})
        url = extracted_url.group(0)

    new_recipe, extras = await scraper.scrape(url, html)

    if not new_recipe:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    new_recipe.id = uuid4()
    logger = get_logger()
    logger.debug(f"Image {new_recipe.image}")

    recipe_data_service = RecipeDataService(new_recipe.id)

    try:
        if new_recipe.image and isinstance(new_recipe.image, list):
            new_recipe.image = new_recipe.image[0]
        await recipe_data_service.scrape_image(new_recipe.image)  # type: ignore

        if new_recipe.name is None:
            new_recipe.name = "Untitled"

        new_recipe.slug = slugify(new_recipe.name)
        new_recipe.image = cache.new_key(4)
    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        new_recipe.image = "no image"

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = f"No Recipe Name Found - {uuid4()!s}"
        new_recipe.slug = slugify(new_recipe.name)

    return new_recipe, extras
