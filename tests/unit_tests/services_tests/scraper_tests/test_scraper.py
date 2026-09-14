import pytest

from mealie.lang.providers import get_locale_provider
from mealie.schema.recipe.recipe import Recipe
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


@pytest.mark.asyncio
async def test_create_from_html_adds_scraped_step_images_as_assets(monkeypatch):
    extras = ScrapedExtras()
    extras.set_step_images(
        [
            ["https://i2.chuimg.com/step-1.gif?imageView2/2/w/300"],
            ["https://i2.chuimg.com/step-2.gif?imageView2/2/w/300"],
        ]
    )

    async def fake_scrape(self, url, html=None, on_progress=None):
        return (
            Recipe(
                name="Xiachufang Test Recipe",
                image=None,
                recipe_instructions=[
                    {"text": "First step"},
                    {"text": "Second step"},
                ],
            ),
            extras,
        )

    async def fake_download_asset(self, image_url, file_name):
        return self.dir_assets / file_name

    monkeypatch.setattr(RecipeScraper, "scrape", fake_scrape)
    monkeypatch.setattr(
        "mealie.services.recipe.recipe_data_service.RecipeDataService.download_asset",
        fake_download_asset,
    )

    translator = get_locale_provider()

    recipe, returned_extras = await scraper.create_from_html(
        "https://www.xiachufang.com/recipe/106382966/",
        repos=None,  # type: ignore[arg-type]
        translator=translator,
        html="<html></html>",
    )

    assert returned_extras is extras

    assert recipe.assets is not None
    assert len(recipe.assets) == 2

    assert recipe.assets[0].file_name == "step-1-1.gif"
    assert recipe.assets[1].file_name == "step-2-1.gif"

    assert f"/api/media/recipes/{recipe.id}/assets/step-1-1.gif" in recipe.recipe_instructions[0].text
    assert f"/api/media/recipes/{recipe.id}/assets/step-2-1.gif" in recipe.recipe_instructions[1].text
