from collections.abc import Awaitable, Callable
from enum import StrEnum
from re import search as regex_search
from uuid import uuid4

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import cache
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import Recipe, RecipeAsset
from mealie.schema.recipe.recipe import create_recipe_slug
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraped_extras import ScrapedExtras

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
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                {"details": ParserErrors.BAD_RECIPE_DATA.value},
            )

        url = extracted_url.group(0)

    new_recipe, extras = await scraper.scrape(
        url,
        html,
        on_progress=on_progress,
    )

    if not new_recipe:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"details": ParserErrors.BAD_RECIPE_DATA.value},
        )

    new_recipe.id = uuid4()

    logger = get_logger()
    logger.debug(f"Image {new_recipe.image}")

    recipe_data_service = RecipeDataService(new_recipe.id)

    # Download the main recipe image.
    try:
        if new_recipe.image:
            if isinstance(new_recipe.image, list):
                new_recipe.image = new_recipe.image[0]

            if on_progress:
                await on_progress(translator.t("recipe.create-progress.downloading-image"))

            await recipe_data_service.scrape_image(new_recipe.image)  # type: ignore

    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        new_recipe.image = "no image"

    if new_recipe.name is None:
        new_recipe.name = "Untitled"

    new_recipe.slug = create_recipe_slug(new_recipe.name)

    if new_recipe.image != "no image":
        new_recipe.image = cache.new_key(4)

    # Download scraped step images and store them as normal recipe assets.
    if extras:
        step_images = extras.get_step_images()

        for index, images in enumerate(step_images):
            if index >= len(new_recipe.recipe_instructions):
                break

            for image_index, image_url in enumerate(images):
                extension = image_url.split("?")[0].split(".")[-1].lower()

                if extension not in {
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "webp",
                    "bmp",
                    "avif",
                }:
                    extension = "jpg"

                file_name = f"step-{index + 1}-{image_index + 1}.{extension}"

                asset_path = await recipe_data_service.download_asset(
                    image_url,
                    file_name,
                )

                if asset_path:
                    asset = RecipeAsset(
                        name=file_name,
                        icon="mdi-file-image",
                        file_name=file_name,
                    )

                    if new_recipe.assets is None:
                        new_recipe.assets = []

                    new_recipe.assets.append(asset)

                    asset_url = f"/api/media/recipes/{new_recipe.id}/assets/{file_name}"

                    new_recipe.recipe_instructions[index].text += f'<img src="{asset_url}" height="100%" width="100%"/>'

    if new_recipe.name is None or new_recipe.name == "":
        new_recipe.name = f"No Recipe Name Found - {uuid4()!s}"
        new_recipe.slug = create_recipe_slug(new_recipe.name)

    return new_recipe, extras
