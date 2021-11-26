from __future__ import annotations

from typing import Type

from mealie.schema.recipe.recipe import Recipe

from .scraper_strategies import ABCScraperStrategy, RecipeScraperOpenGraph, RecipeScraperPackage


class RecipeScraper:
    """
    Scrapes recipes from the web.
    """

    # List of recipe scrapers. Note that order matters
    scrapers: list[Type[ABCScraperStrategy]]

    def __init__(self, scrapers: list[Type[ABCScraperStrategy]] = None) -> None:
        if scrapers is None:
            scrapers = [
                RecipeScraperPackage,
                RecipeScraperOpenGraph,
            ]

        self.scrapers = scrapers

    def scrape(self, url: str) -> Recipe | None:
        """
        Scrapes a recipe from the web.
        """

        for scraper in self.scrapers:
            scraper = scraper(url)
            recipe = scraper.parse()

            if recipe is not None:
                return recipe

        return None
