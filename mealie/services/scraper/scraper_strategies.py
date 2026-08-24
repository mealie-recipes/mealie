import asyncio
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

import extruct
from fastapi import HTTPException, status
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, scrape_html
from slugify import slugify
from w3lib.html import get_base_url

from mealie.core import exceptions
from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.openai.recipe import OpenAIRecipe
from mealie.schema.recipe.recipe import Recipe, RecipeStep
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.services.openai import OpenAIService, transcription
from mealie.services.recipe.import_workflow import (
    RecipeImportWorkflow,
    WorkflowContext,
    WorkflowInput,
    WorkflowOptions,
)
from mealie.services.scraper.scraped_extras import ScrapedExtras

from . import cleaner

# Re-exported for backwards compatibility with existing importers (e.g. recipe route error handling).
# safe_scrape_html lives in `fetch` so the import workflow can fetch pages without importing this module.
from .fetch import (  # noqa: F401
    BROWSER_IMPERSONATIONS,
    SCRAPER_TIMEOUT,
    ForceTimeoutException,
    safe_scrape_html,
)

logger = get_logger()


class ABCScraperStrategy(ABC):
    """
    Abstract class for all recipe parsers.
    """

    url: str

    def __init__(
        self,
        url: str,
        translator: Translator,
        repos: AllRepositories,
        raw_html: str | None = None,
        include_tags: bool = False,
        include_categories: bool = False,
    ) -> None:
        self.logger = get_logger()
        self.url = url
        self.raw_html = raw_html
        self.translator = translator
        self.repos = repos

        # only used by strategies that have to ask for organizers, rather than reading them
        # out of the page's structured data
        self.include_tags = include_tags
        self.include_categories = include_categories

    @abstractmethod
    def can_scrape(self) -> bool: ...

    @abstractmethod
    async def get_html(self, url: str) -> str: ...

    @abstractmethod
    async def parse(
        self, on_progress: Callable[[str], Awaitable[None]] | None = None
    ) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        """Parse a recipe from a web URL.

        Args:
            recipe_url (str): Full URL of the recipe to scrape.

        Returns:
            Recipe: Recipe object.
        """
        ...


class RecipeScraperPackage(ABCScraperStrategy):
    def can_scrape(self) -> bool:
        return bool(self.url or self.raw_html)

    @staticmethod
    def ld_json_to_html(ld_json: str) -> str:
        return (
            "<!DOCTYPE html><html><head>"
            f'<script type="application/ld+json">{ld_json}</script>'
            "</head><body></body></html>"
        )

    async def get_html(self, url: str) -> str:
        return self.raw_html or await safe_scrape_html(url)

    def clean_scraper(self, scraped_data: SchemaScraperFactory.SchemaScraper, url: str) -> tuple[Recipe, ScrapedExtras]:
        def try_get_default(
            func_call: Callable | None,
            get_attr: str,
            default: Any,
            clean_func=None,
            **clean_func_kwargs,
        ):
            value = default

            if func_call:
                try:
                    value = func_call()
                except Exception:
                    self.logger.error(f"Error parsing recipe func_call for '{get_attr}'")

            if value == default:
                try:
                    value = scraped_data.schema.data.get(get_attr)
                except Exception:
                    self.logger.error(f"Error parsing recipe attribute '{get_attr}'")

            if clean_func:
                value = clean_func(value, **clean_func_kwargs)

            return value

        def get_instructions() -> list[RecipeStep]:
            instruction_as_text = try_get_default(
                scraped_data.instructions,
                "recipeInstructions",
                ["No Instructions Found"],
            )

            self.logger.debug(f"Scraped Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

            instruction_as_text = cleaner.clean_instructions(instruction_as_text)

            self.logger.debug(f"Cleaned Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

            try:
                return [RecipeStep(title="", text=x.get("text")) for x in instruction_as_text]
            except TypeError:
                return []

        def get_notes() -> list[RecipeNote]:
            """Extract notes from schema.org recipe data and convert to RecipeNote objects"""
            notes_data = try_get_default(None, "notes", None)

            if not notes_data or not isinstance(notes_data, list):
                return []

            cleaned_notes = []
            for note in notes_data:
                if not isinstance(note, dict):
                    continue

                if text := note.get("text"):
                    cleaned_notes.append(
                        RecipeNote(
                            title=cleaner.clean_string(note.get("title", "")),
                            text=cleaner.clean_string(text),
                        )
                    )

            return cleaned_notes

        cook_time = try_get_default(
            None, "performTime", None, cleaner.clean_time, translator=self.translator
        ) or try_get_default(scraped_data.cook_time, "cookTime", None, cleaner.clean_time, translator=self.translator)

        extras = ScrapedExtras()

        extras.set_tags(try_get_default(scraped_data.keywords, "keywords", "", cleaner.clean_tags))
        extras.set_categories(try_get_default(scraped_data.category, "recipeCategory", "", cleaner.clean_categories))

        recipe = Recipe(
            name=try_get_default(scraped_data.title, "name", "No Name Found", cleaner.clean_string),
            slug="",
            image=try_get_default(scraped_data.image, "image", None, cleaner.clean_image),
            description=try_get_default(scraped_data.description, "description", "", cleaner.clean_string),
            nutrition=try_get_default(scraped_data.nutrients, "nutrition", None, cleaner.clean_nutrition),
            recipe_yield=try_get_default(scraped_data.yields, "recipeYield", "1", cleaner.clean_string),
            recipe_ingredient=try_get_default(
                scraped_data.ingredients,
                "recipeIngredient",
                [""],
                cleaner.clean_ingredients,
            ),
            recipe_instructions=get_instructions(),
            total_time=try_get_default(
                scraped_data.total_time, "totalTime", None, cleaner.clean_time, translator=self.translator
            ),
            prep_time=try_get_default(
                scraped_data.prep_time, "prepTime", None, cleaner.clean_time, translator=self.translator
            ),
            perform_time=cook_time,
            org_url=url or try_get_default(None, "url", None, cleaner.clean_string),
            notes=get_notes(),
        )

        return recipe, extras

    async def scrape_url(self) -> SchemaScraperFactory.SchemaScraper | Any | None:
        recipe_html = await self.get_html(self.url)

        try:
            # scrape_html requires a URL, but we might not have one, so we default to a dummy URL
            scraped_schema = scrape_html(recipe_html, org_url=self.url or "https://example.com", supported_only=False)
        except (NoSchemaFoundInWildMode, AttributeError):
            self.logger.error(f"Recipe Scraper was unable to extract a recipe from {self.url}")
            return None

        except ConnectionError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"details": "CONNECTION_ERROR"}) from e

        # Check to see if the recipe is valid
        try:
            ingredients = scraped_schema.ingredients()
        except Exception:
            ingredients = []

        try:
            instruct: list | str = scraped_schema.instructions()
        except Exception:
            instruct = []

        if instruct or ingredients:
            return scraped_schema

        self.logger.debug(f"Recipe Scraper [Package] was unable to extract a recipe from {self.url}")
        return None

    async def parse(self, on_progress: Callable[[str], Awaitable[None]] | None = None):
        """
        Parse a recipe from a given url.
        """

        if on_progress:
            await on_progress(self.translator.t("recipe.create-progress.extracting-recipe-data"))

        scraped_data = await self.scrape_url()

        if scraped_data is None:
            return None

        return self.clean_scraper(scraped_data, self.url)


class RecipeScraperOpenAI(ABCScraperStrategy):
    """
    Extracts a recipe from a URL using AI, by running the recipe import workflow over the
    page's contents rather than trying to scrape it directly.
    """

    def can_scrape(self) -> bool:
        settings = self.repos.group_ai_provider_settings.get_one(self.repos.group_id)
        return bool(settings and settings.ai_enabled and (self.url or self.raw_html))

    async def get_html(self, url: str) -> str:
        # required by the base class, but unused: the workflow fetches the page itself
        return self.raw_html or await safe_scrape_html(url)

    def build_context(self, on_progress: Callable[[str], Awaitable[None]] | None = None) -> WorkflowContext:
        return WorkflowContext(
            # the HTML belongs to the URL, so it's passed as the page's content rather than as
            # extra material, which would compile the same page twice
            input=WorkflowInput(page_content=self.raw_html, url=self.url),
            options=WorkflowOptions(
                # organizers are only worth asking for if the caller intends to use them, and
                # they're reported back through ScrapedExtras so the caller stays in control
                resolve_organizers=self.include_tags or self.include_categories,
                attach_organizers=False,
            ),
            repos=self.repos,
            translator=self.translator,
            ai=OpenAIService(self.repos),
            on_progress=on_progress,
        )

    async def parse(self, on_progress: Callable[[str], Awaitable[None]] | None = None):
        ctx = self.build_context(on_progress)
        result = await RecipeImportWorkflow().run(ctx)

        extras = ScrapedExtras()
        if ctx.organizer_names:
            # normalized the same way as organizers read out of a page's structured data
            extras.set_tags(cleaner.clean_tags(ctx.organizer_names.tags))
            extras.set_categories(cleaner.clean_categories(ctx.organizer_names.categories))

        return result.recipe, extras


class RecipeScraperOpenAITranscription(ABCScraperStrategy):
    def can_scrape(self) -> bool:
        if not self.url:
            return False

        settings = self.repos.group_ai_provider_settings.get_one(self.repos.group_id)
        if not (settings and settings.audio_provider_enabled):
            return False

        # Check if we can actually download something to transcribe
        return transcription.is_video_url(self.url)

    async def get_html(self, url: str) -> str:
        return self.raw_html or ""  # we don't use HTML with this scraper since we use ytdlp

    async def parse(
        self,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        openai_service = OpenAIService(self.repos)

        with get_temporary_path() as temp_path:
            if on_progress:
                await on_progress(self.translator.t("recipe.create-progress.downloading-video"))

            video_data = await asyncio.to_thread(transcription.download_video, self.url, temp_path)

            async def report_transcribing() -> None:
                if on_progress:
                    await on_progress(self.translator.t("recipe.create-progress.transcribing-audio-with-ai"))

            video_data["transcription"] = await transcription.resolve_transcription(
                video_data, openai_service, before_transcribe=report_transcribing
            )

        if not video_data["transcription"]:
            self.logger.error("Could not extract a transcript (no data)")
            return None, None

        self.logger.debug(f"Transcription: {video_data['transcription'][:200]}...")
        prompt = openai_service.get_prompt("recipes.parse-recipe-video")

        message_parts = [
            f"Title: {video_data['title']}",
            f"Description: {video_data['description']}",
            f"Transcription: {video_data['transcription']}",
        ]

        if on_progress:
            await on_progress(self.translator.t("recipe.create-progress.creating-recipe-from-transcript-with-ai"))

        try:
            response = await openai_service.get_response(prompt, "\n".join(message_parts), response_schema=OpenAIRecipe)
        except exceptions.RateLimitError:
            raise
        except Exception as e:
            raise exceptions.OpenAIServiceError(f"Failed to extract recipe from video: {e}") from e

        if not response:
            raise exceptions.OpenAIServiceError("OpenAI returned an empty response when extracting recipe")

        recipe = Recipe(
            name=response.name,
            slug="",
            description=response.description,
            recipe_yield=response.recipe_yield,
            total_time=response.total_time,
            prep_time=response.prep_time,
            perform_time=response.perform_time,
            recipe_ingredient=[
                RecipeIngredient(title=ingredient.title, note=ingredient.text)
                for ingredient in response.ingredients
                if ingredient.text
            ],
            recipe_instructions=[
                RecipeStep(title=instruction.title, text=instruction.text)
                for instruction in response.instructions
                if instruction.text
            ],
            notes=[RecipeNote(title=note.title or "", text=note.text) for note in response.notes if note.text],
            image=video_data["thumbnail_url"] or None,
            org_url=self.url,
        )

        self.logger.info(f"Successfully extracted recipe from video: {video_data['title']}")
        return recipe, ScrapedExtras()


class RecipeScraperOpenGraph(ABCScraperStrategy):
    def can_scrape(self) -> bool:
        return bool(self.url or self.raw_html)

    async def get_html(self, url: str) -> str:
        return self.raw_html or await safe_scrape_html(url)

    def get_recipe_fields(self, html) -> dict | None:
        """
        Get the recipe fields from the Open Graph data.
        """

        def og_field(properties: dict, field_name: str) -> str:
            return next((val for name, val in properties if name == field_name), "")

        def og_fields(properties: list[tuple[str, str]], field_name: str) -> list[str]:
            return list({val for name, val in properties if name == field_name})

        base_url = get_base_url(html, self.url)
        data = extruct.extract(html, base_url=base_url, errors="log")
        try:
            properties = data["opengraph"][0]["properties"]
        except Exception:
            return None

        return {
            "name": og_field(properties, "og:title"),
            "description": og_field(properties, "og:description"),
            "image": og_field(properties, "og:image"),
            "recipeYield": "",
            "recipeIngredient": ["Could not detect ingredients"],
            "recipeInstructions": [{"text": "Could not detect instructions"}],
            "slug": slugify(og_field(properties, "og:title")),
            "orgURL": self.url or og_field(properties, "og:url"),
            "categories": [],
            "tags": og_fields(properties, "og:article:tag"),
            "dateAdded": None,
            "notes": [],
            "extras": [],
        }

    async def parse(
        self,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ):
        """
        Parse a recipe from a given url.
        """

        if on_progress:
            await on_progress(self.translator.t("recipe.create-progress.creating-recipe-from-webpage-data"))

        html = await self.get_html(self.url)

        og_data = self.get_recipe_fields(html)

        if og_data is None:
            return None

        return Recipe(**og_data), ScrapedExtras()
