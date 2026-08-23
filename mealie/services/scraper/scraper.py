from collections.abc import Awaitable, Callable
from enum import StrEnum
from re import search as regex_search
from uuid import uuid4

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import cache
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import create_recipe_slug
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraped_extras import ScrapedExtras

from .cleaner import NO_IMAGE
from .recipe_scraper import RecipeScraper


class ParserErrors(StrEnum):
    BAD_RECIPE_DATA = "BAD_RECIPE_DATA"
    NO_RECIPE_DATA = "NO_RECIPE_DATA"
    CONNECTION_ERROR = "CONNECTION_ERROR"


async def create_from_html(
    url: str,
    repos: AllRepositories,
    translator: Translator,
    html: str | None = None,
    on_progress: Callable[[str], Awaitable[None]] | None = None,
    include_tags: bool = False,
    include_categories: bool = False,
) -> tuple[Recipe, ScrapedExtras | None]:
    """Main entry point for generating a recipe from a URL. Pass in a URL and
    a Recipe object will be returned if successful. Optionally pass in the HTML to skip fetching it.

    Args:
        url (str): a valid string representing a URL
        html (str | None): optional HTML string to skip network request. Defaults to None.
        on_progress: optional async callable invoked with a status message at each stage.

    Returns:
        Recipe: Recipe Object
    """
    scraper = RecipeScraper(repos, translator)

    if not html:
        extracted_url = regex_search(r"(https?://|www\.)[^\s]+", url)
        if not extracted_url:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})
        url = extracted_url.group(0)

    new_recipe, extras = await scraper.scrape(
        url,
        html,
        on_progress=on_progress,
        include_tags=include_tags,
        include_categories=include_categories,
    )

    if not new_recipe:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": ParserErrors.BAD_RECIPE_DATA.value})

    new_recipe = await finalize_scraped_recipe(new_recipe, translator, on_progress=on_progress)
    return new_recipe, extras


async def finalize_scraped_recipe(
    recipe: Recipe,
    translator: Translator,
    on_progress: Callable[[str], Awaitable[None]] | None = None,
) -> Recipe:
    """Assigns an id to a freshly scraped recipe, downloads its image, and guarantees it has a name and slug.

    The recipe is not persisted; that's up to the caller.
    """

    recipe.id = uuid4()
    logger = get_logger()
    logger.debug(f"Image {recipe.image}")

    recipe_data_service = RecipeDataService(recipe.id)

    try:
        if isinstance(recipe.image, list):
            recipe.image = recipe.image[0] if recipe.image else None

        # NO_IMAGE is a placeholder rather than a URL, so there's nothing to download for it
        if recipe.image and recipe.image != NO_IMAGE:
            if on_progress:
                await on_progress(translator.t("recipe.create-progress.downloading-image"))
            await recipe_data_service.scrape_image(recipe.image)  # type: ignore

        if recipe.name is None:
            recipe.name = "Untitled"

        recipe.slug = create_recipe_slug(recipe.name)
        recipe.image = cache.new_key(4)
    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        recipe.image = NO_IMAGE

    if recipe.name is None or recipe.name == "":
        recipe.name = f"No Recipe Name Found - {uuid4()!s}"
        recipe.slug = create_recipe_slug(recipe.name)

    return recipe
