from mealie.lang.providers import Translator
from mealie.schema.recipe.recipe import Recipe
from mealie.services.scraper.scraped_extras import ScrapedExtras

from .scraper_strategies import ABCScraperStrategy, RecipeScraperOpenGraph, RecipeScraperPackage

DEFAULT_SCRAPER_STRATEGIES: list[type[ABCScraperStrategy]] = [RecipeScraperPackage, RecipeScraperOpenGraph]


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

    async def scrape(self, url: str) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        """
        Scrapes a recipe from the web.
        """

        for scraper_type in self.scrapers:
            scraper = scraper_type(url, self.translator)
            result = await scraper.parse()

            if result is not None:
                return result

        return None, None
