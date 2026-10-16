from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import UUID4

from mealie.lang.providers import get_locale_provider
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    IngredientUnit,
    ParsedIngredient,
    RecipeIngredient,
)
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper import scraper
from mealie.services.scraper.recipe_scraper import RecipeScraper
from mealie.services.scraper.scraped_extras import ScrapedExtras


@pytest.mark.asyncio
async def test_create_from_html_truncates_long_slug(monkeypatch):
    """A recipe scraped with an excessively long name must yield a slug short enough
    to be used as a filesystem directory name.

    Regression test for GH #7662: scraping (e.g. an Instagram caption) dumped the entire
    text into the recipe name. The scraper used a raw ``slugify`` instead of the shared
    ``create_recipe_slug`` helper, so the persisted slug could exceed the OS 255-byte
    filename limit. Editing/saving the recipe then raised an uncaught
    ``OSError: [Errno 36] File name too long`` in ``RecipeService.check_assets``.
    """
    # ~1300 characters, mirroring the caption-as-title data from the bug report
    long_name = "High Protein Low Calorie Recipes Smash Or Pass " * 28

    async def fake_scrape(self, url, html=None, on_progress=None, **kwargs):
        return Recipe(name=long_name), ScrapedExtras()

    monkeypatch.setattr(RecipeScraper, "scrape", fake_scrape)

    translator = get_locale_provider()
    recipe, _ = await scraper.create_from_html(
        "https://example.com/recipe",
        repos=None,  # type: ignore[arg-type]
        translator=translator,
        html="<html></html>",
    )

    # The full title is preserved (name column is unbounded)...
    assert recipe.name == long_name
    # ...but the slug is truncated to a filesystem-safe length.
    assert 0 < len(recipe.slug) <= 250


@pytest.mark.parametrize(
    ("scraped_image", "download_result", "expect_key"),
    [
        pytest.param("https://example.com/img.jpg", Path("/images/original.webp"), True, id="image-downloaded"),
        pytest.param("https://example.com/img.jpg", None, False, id="download-failed"),
        pytest.param("no image", None, False, id="placeholder-url"),
        pytest.param(None, None, False, id="no-image-url"),
    ],
)
@pytest.mark.asyncio
async def test_finalize_only_stamps_a_cache_key_when_an_image_landed(
    monkeypatch, scraped_image, download_result, expect_key
):
    """`recipe.image` must stay empty unless a file actually reached the disk.

    The frontend reads the presence of this cache key as "this recipe has a picture" and
    skips the request entirely when it is empty. Stamping a key regardless of whether the
    download succeeded is what left recipes asking the media route for a file that 404s on
    every single render (mealie-recipes/mealie#8271, GH #4804).
    """

    async def fake_scrape_image(self, image_url):
        return download_result

    monkeypatch.setattr(RecipeDataService, "scrape_image", fake_scrape_image)

    recipe = await scraper.finalize_scraped_recipe(
        Recipe(name="Test Recipe", image=scraped_image),
        get_locale_provider(),
    )

    assert bool(recipe.image) is expect_key


@pytest.mark.asyncio
async def test_parse_unstructured_ingredients_keeps_only_matched_units_and_foods(monkeypatch):
    """Regression test for the Magimix import (user-reported): a scraped recipe's ingredients
    arrive as a single unstructured string per ingredient (schema.org has no structured
    quantity/unit/food), so they previously stayed that way forever unless the user manually ran
    the "Parse Ingredients" dialog. This exercises the auto-parse hook added to close that gap.

    Two cases, driven by a stubbed parser so this doesn't depend on the real brute-force parser's
    text handling: a unit the group's database already has (must be kept, with quantity), and a
    food name nothing matches (must NOT be kept as-is - saving a recipe requires every unit/food
    to reference an existing row by id - its text must be folded back into the note instead).
    """
    matched_unit = IngredientUnit(id=uuid4(), name="gram")

    async def fake_parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [
            ParsedIngredient(
                input=ingredients[0],
                ingredient=RecipeIngredient(
                    quantity=7,
                    unit=matched_unit,
                    food=CreateIngredientFood(name="unmatched yeast"),  # id=None: not in the db
                    note="",
                    original_text=ingredients[0],
                ),
            ),
        ]

    monkeypatch.setattr(
        "mealie.services.scraper.scraper.get_parser", lambda *a, **kw: type("P", (), {"parse": fake_parse})()
    )

    recipe = Recipe(name="Test", recipe_ingredient=["7 g de levure sèche de boulanger"])
    repos = AllRepositories(session=None, group_id=UUID4(str(uuid4())))  # type: ignore[arg-type]

    await scraper._parse_unstructured_ingredients(recipe, repos, get_locale_provider())

    ingredient = recipe.recipe_ingredient[0]
    assert ingredient.quantity == 7
    assert ingredient.unit is not None and ingredient.unit.id == matched_unit.id
    assert ingredient.food is None
    assert "unmatched yeast" in (ingredient.note or "")


@pytest.mark.asyncio
async def test_parse_unstructured_ingredients_skips_already_structured_ingredients():
    """An ingredient that already has a quantity/unit/food (e.g. from the AI importer, which
    extracts these directly) must be left exactly as given - it's not unstructured scraper
    output, so re-running it through the brute parser would only risk overwriting good data."""
    repos = AllRepositories(session=None, group_id=UUID4(str(uuid4())))  # type: ignore[arg-type]
    already_structured = RecipeIngredient(quantity=2, note="already parsed")
    recipe = Recipe(name="Test")
    recipe.recipe_ingredient = [already_structured]

    await scraper._parse_unstructured_ingredients(recipe, repos, get_locale_provider())

    assert recipe.recipe_ingredient[0] is already_structured


@pytest.mark.asyncio
async def test_parse_unstructured_ingredients_noop_without_repos():
    """Guard for callers (or future call sites) that don't have a group to match against -
    must not raise, and must leave the raw scraped note untouched."""
    recipe = Recipe(name="Test", recipe_ingredient=["2 eggs"])

    await scraper._parse_unstructured_ingredients(recipe, None, get_locale_provider())

    assert recipe.recipe_ingredient[0].note == "2 eggs"
    assert recipe.recipe_ingredient[0].quantity == 0
