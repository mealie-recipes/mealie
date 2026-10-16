from collections.abc import Awaitable, Callable
from enum import StrEnum
from re import search as regex_search
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import cache
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import create_recipe_slug
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, RegisteredParser
from mealie.services.parser_services import get_parser
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

    new_recipe = await finalize_scraped_recipe(new_recipe, translator, repos=repos, on_progress=on_progress)
    return new_recipe, extras


async def _parse_unstructured_ingredients(
    recipe: Recipe, repos: AllRepositories | None, translator: Translator
) -> None:
    """Give scraped ingredients a structured quantity/unit/food, best-effort.

    schema.org (what every site's recipe markup follows) only ever gives an ingredient as one
    unstructured line of text, so a freshly scraped recipe's ingredients come back as a bare
    `note` with no quantity/unit/food at all - only ever filled in if the user later opens the
    "Parse Ingredients" dialog by hand. Running them through the brute-force parser here gives a
    structured starting point instead, without requiring that extra step. The brute parser (not
    the NLP one, which is English-only) is locale-agnostic and makes no network/AI calls.

    Only ingredients with no quantity, unit or food are touched - an ingredient a caller already
    populated (e.g. the AI importer, which extracts these directly) is left exactly as given. A
    line the parser can't make sense of is left as it was, same as before this existed.

    A unit or food the parser named but couldn't match to one already in the group's database is
    *not* kept on the ingredient: saving a recipe requires every unit/food to reference an
    existing row by id (nothing here creates new ones - unlike the interactive "Parse
    Ingredients" dialog, there's no user to review a new food/unit name before it's added to
    their library), so an unmatched one would otherwise make the whole import fail to save. Its
    text is folded back into the note instead, so nothing is silently dropped.
    """
    if repos is None or not isinstance(repos.group_id, UUID) or not recipe.recipe_ingredient:
        return

    unstructured = [
        ingredient
        for ingredient in recipe.recipe_ingredient
        if ingredient.note and not ingredient.quantity and not ingredient.unit and not ingredient.food
    ]
    if not unstructured:
        return

    parser = get_parser(RegisteredParser.brute, repos.group_id, repos.session, translator)
    parsed = await parser.parse([ingredient.note or "" for ingredient in unstructured])

    for ingredient, result in zip(unstructured, parsed, strict=True):
        parsed_ingredient = result.ingredient
        unmatched = [
            part.name
            for part in (parsed_ingredient.unit, parsed_ingredient.food)
            if part is not None and part.id is None
        ]

        ingredient.quantity = parsed_ingredient.quantity
        ingredient.unit = parsed_ingredient.unit if parsed_ingredient.unit and parsed_ingredient.unit.id else None
        ingredient.food = parsed_ingredient.food if parsed_ingredient.food and parsed_ingredient.food.id else None
        ingredient.note = ", ".join(filter(None, [*unmatched, parsed_ingredient.note]))
        ingredient.original_text = parsed_ingredient.original_text or ingredient.note


def _merge_key(ingredient: RecipeIngredient) -> tuple | None:
    """A key two ingredients must share to be considered the same measurement, or None if this
    ingredient is never safe to merge (a sub-recipe reference, or one with substitutions - either
    could silently drop information a plain quantity sum wouldn't)."""
    if ingredient.referenced_recipe is not None or ingredient.substitutions:
        return None

    food = ingredient.food
    unit = ingredient.unit
    return (
        ingredient.title,
        food.id if food and food.id else food.name if food else None,
        unit.id if unit and unit.id else unit.name if unit else None,
        (ingredient.note or "").strip().lower(),
    )


def _merge_redundant_ingredients(recipe: Recipe) -> None:
    """Combine ingredient lines that are really just the same measurement split in two.

    Scraped sites sometimes list the same ingredient on separate lines because it's used at two
    points in the method (e.g. "2 eggs" in the dough and, elsewhere, "1 egg" for the egg wash).
    Once parsed, those become two lines for the same food with no distinguishing note, which reads
    as a mistake rather than two separate uses - merging them into one "3 eggs" line matches what
    a shopping list for this recipe would actually say.

    Only lines with the same food, unit, note and section title are merged - any difference in
    note is treated as the recipe intentionally keeping them apart, and is left untouched.
    """
    merged: dict[tuple, RecipeIngredient] = {}
    result: list[RecipeIngredient] = []

    for ingredient in recipe.recipe_ingredient:
        key = _merge_key(ingredient)
        if key is None:
            result.append(ingredient)
            continue

        if existing := merged.get(key):
            existing.quantity = (existing.quantity or 0) + (ingredient.quantity or 0)
            if ingredient.original_text and ingredient.original_text not in (existing.original_text or ""):
                existing.original_text = "; ".join(filter(None, [existing.original_text, ingredient.original_text]))
            continue

        merged[key] = ingredient
        result.append(ingredient)

    recipe.recipe_ingredient = result


async def finalize_scraped_recipe(
    recipe: Recipe,
    translator: Translator,
    repos: AllRepositories | None = None,
    on_progress: Callable[[str], Awaitable[None]] | None = None,
) -> Recipe:
    """Assigns an id to a freshly scraped recipe, downloads its image, and guarantees it has a name and slug.

    The recipe is not persisted; that's up to the caller.
    """

    recipe.id = uuid4()

    await _parse_unstructured_ingredients(recipe, repos, translator)
    _merge_redundant_ingredients(recipe)
    logger = get_logger()
    logger.debug(f"Image {recipe.image}")

    recipe_data_service = RecipeDataService(recipe.id)

    image_written = False

    try:
        if isinstance(recipe.image, list):
            recipe.image = recipe.image[0] if recipe.image else None

        # NO_IMAGE is a placeholder rather than a URL, so there's nothing to download for it
        if recipe.image and recipe.image != NO_IMAGE:
            if on_progress:
                await on_progress(translator.t("recipe.create-progress.downloading-image"))
            image_written = await recipe_data_service.scrape_image(recipe.image) is not None  # type: ignore

        if recipe.name is None:
            recipe.name = "Untitled"

        recipe.slug = create_recipe_slug(recipe.name)
    except Exception as e:
        recipe_data_service.logger.exception(f"Error Scraping Image: {e}")
        image_written = False

    # `image` is the cache key the frontend uses to decide whether to request an image at
    # all, so it must stay empty unless a file actually landed on disk. Stamping a key for
    # a recipe with no image is what makes every render ask for a file that 404s.
    recipe.image = cache.new_key(4) if image_written else None

    if recipe.name is None or recipe.name == "":
        recipe.name = f"No Recipe Name Found - {uuid4()!s}"
        recipe.slug = create_recipe_slug(recipe.name)

    return recipe
