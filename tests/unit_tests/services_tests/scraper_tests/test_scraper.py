import pytest

from mealie.lang.providers import get_locale_provider
from mealie.schema.recipe.recipe import Recipe
from mealie.services.scraper import scraper
from mealie.services.scraper.recipe_scraper import RecipeScraper
from mealie.services.scraper.scraped_extras import ScrapedExtras
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage


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

    async def fake_scrape(self, url, html=None, on_progress=None):
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


class _FakeSchema:
    def __init__(self, data: dict):
        self.data = data


class _FakeScrapedData:
    """Stand-in for a `recipe_scrapers` SchemaScraper, exercising only `instructions()`.

    Every other scraper method resolves via `__getattr__` to a no-op so `clean_scraper`'s
    `try_get_default` calls succeed and fall through to the (empty) `schema.data` dict,
    instead of raising `AttributeError` on an unimplemented method.
    """

    def __init__(self, instructions_data):
        self._instructions_data = instructions_data
        self.schema = _FakeSchema({})

    def __getattr__(self, name):
        return lambda *args, **kwargs: None

    def instructions(self):
        return self._instructions_data


def test_clean_scraper_preserves_instruction_title_and_summary():
    """Regression test for PR #7785 item 4: `recipeInstructions[].title`/`.summary` must
    survive the full parse -> clean -> RecipeStep pipeline in `RecipeScraperPackage.clean_scraper`,
    not just in the lower-level `cleaner.clean_instructions` unit test.
    """
    scraped_data = _FakeScrapedData(
        [
            {"title": "Make the Batter", "summary": "Mix dry and wet ingredients", "text": "Whisk everything together."},
            {"title": "Cook", "summary": "Pan fry until golden", "text": "Heat oil and fry for 4-5 minutes per side."},
        ]
    )

    translator = get_locale_provider()
    scraper = RecipeScraperPackage(url="https://example.com/recipe", translator=translator, repos=None)  # type: ignore[arg-type]
    recipe, _ = scraper.clean_scraper(scraped_data, url="https://example.com/recipe")  # type: ignore[arg-type]

    assert len(recipe.recipe_instructions) == 2

    assert recipe.recipe_instructions[0].title == "Make the Batter"
    assert recipe.recipe_instructions[0].summary == "Mix dry and wet ingredients"
    assert recipe.recipe_instructions[0].text == "Whisk everything together."

    assert recipe.recipe_instructions[1].title == "Cook"
    assert recipe.recipe_instructions[1].summary == "Pan fry until golden"
    assert recipe.recipe_instructions[1].text == "Heat oil and fry for 4-5 minutes per side."
