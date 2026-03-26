from collections.abc import Awaitable, Callable

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.schema.recipe.recipe import Recipe
from mealie.services.scraper import cleaner
from mealie.services.scraper.scraped_extras import ScrapedExtras

from .scraper_strategies import (
    ABCScraperStrategy,
    RecipeScraperOpenAI,
    RecipeScraperOpenAITranscription,
    RecipeScraperOpenGraph,
    RecipeScraperPackage,
    safe_scrape_html,
)

DEFAULT_SCRAPER_STRATEGIES: list[type[ABCScraperStrategy]] = [
    RecipeScraperPackage,
    RecipeScraperOpenAITranscription,
    RecipeScraperOpenAI,
    RecipeScraperOpenGraph,
]


class RecipeScraper:
    """
    Scrapes recipes from the web.
    """

    # List of recipe scrapers. Note that order matters
    scrapers: list[type[ABCScraperStrategy]]

    def __init__(self, translator: Translator, scrapers: list[type[ABCScraperStrategy]] | None = None) -> None:
        if scrapers is None:
            scrapers = DEFAULT_SCRAPER_STRATEGIES

        self.scrapers = scrapers
        self.translator = translator
        self.logger = get_logger()

    async def scrape(
        self,
        url: str,
        html: str | None = None,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        """
        Scrapes a recipe from the web.
        Skips the network request if `html` is provided.
        Optionally reports progress back via `on_progress`.
        """

        if not html:
            if on_progress:
                await on_progress(self.translator.t("recipe.create-progress.fetching-webpage"))

            html = await safe_scrape_html(url)
            if not html:
                return None, None

        for ScraperClass in self.scrapers:
            scraper = ScraperClass(url, self.translator, raw_html=html)
            if not scraper.can_scrape():
                self.logger.debug(f"Skipping {scraper.__class__.__name__}")
                continue

            try:
                result = await scraper.parse(on_progress=on_progress)
            except Exception:
                self.logger.exception(f"Failed to scrape HTML with {scraper.__class__.__name__}")
                result = None

            if result is None or result[0] is None:
                continue

            recipe_result, extras = result
            try:
                recipe = cleaner.clean(recipe_result, self.translator)
            except Exception:
                self.logger.exception(f"Failed to clean recipe data from {scraper.__class__.__name__}")
                continue

            return recipe, extras

        return None, None
