from collections.abc import Awaitable, Callable

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs.safehttp import fetch_via_flaresolverr, resilient_fetch
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.services.scraper import cleaner
from mealie.services.scraper.scraped_extras import ScrapedExtras

from .scraper_strategies import (
    ABCScraperStrategy,
    RecipeScraperOpenAI,
    RecipeScraperOpenAITranscription,
    RecipeScraperOpenGraph,
    RecipeScraperPackage,
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

    def __init__(
        self, repos: AllRepositories, translator: Translator, scrapers: list[type[ABCScraperStrategy]] | None = None
    ) -> None:
        if scrapers is None:
            scrapers = DEFAULT_SCRAPER_STRATEGIES

        self.scrapers = scrapers
        self.repos = repos
        self.translator = translator
        self.logger = get_logger()

    async def scrape(
        self,
        url: str,
        html: str | None = None,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
        include_tags: bool = False,
        include_categories: bool = False,
    ) -> tuple[RecipeDraft, ScrapedExtras] | tuple[None, None]:
        """
        Scrapes a recipe from the web.
        Skips the network request if `html` is provided.
        Optionally reports progress back via `on_progress`.

        `include_tags` and `include_categories` tell strategies whether the caller intends to use
        organizers, so that strategies which have to ask a provider for them can skip the request.
        """

        resolved_url: str | None = None
        can_escalate = False
        if not html:
            if on_progress:
                await on_progress(self.translator.t("recipe.create-progress.fetching-webpage"))

            fetched = await resilient_fetch(url)
            if not fetched or not fetched.text:
                return None, None
            html = fetched.text
            resolved_url = fetched.url
            can_escalate = not fetched.via_flaresolverr

        async def run(
            strategies: list[type[ABCScraperStrategy]], page_html: str, page_url: str | None
        ) -> tuple[RecipeDraft, ScrapedExtras] | tuple[None, None]:
            return await self._scrape_with_strategies(
                strategies,
                url,
                page_html,
                page_url,
                on_progress=on_progress,
                include_tags=include_tags,
                include_categories=include_categories,
            )

        primary = [scraper for scraper in self.scrapers if not scraper.is_fallback]
        fallbacks = [scraper for scraper in self.scrapers if scraper.is_fallback]

        result = await run(primary, html, resolved_url)
        if result[0] is not None:
            return result

        # A page with no recipe is often a JavaScript bot wall served with a 200 status, which the
        # fetch-level challenge detection cannot recognize. FlareSolverr drives a real browser, so
        # retry through it before the fallback strategies accept the bot wall as a recipe.
        if can_escalate:
            solved = await fetch_via_flaresolverr(url)
            if solved is not None and solved.text and solved.text != html:
                html, resolved_url = solved.text, solved.url
                result = await run(primary, html, resolved_url)
                if result[0] is not None:
                    return result

        return await run(fallbacks, html, resolved_url)

    async def _scrape_with_strategies(
        self,
        strategies: list[type[ABCScraperStrategy]],
        url: str,
        html: str,
        resolved_url: str | None,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
        include_tags: bool = False,
        include_categories: bool = False,
    ) -> tuple[RecipeDraft, ScrapedExtras] | tuple[None, None]:
        for ScraperClass in strategies:
            scraper = ScraperClass(
                url,
                self.translator,
                self.repos,
                raw_html=html,
                include_tags=include_tags,
                include_categories=include_categories,
                resolved_url=resolved_url,
            )
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
