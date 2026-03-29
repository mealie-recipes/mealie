import asyncio
import functools
import re
import time
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, TypedDict

import bs4
import extruct
import yt_dlp
from fastapi import HTTPException, status
from httpx import AsyncClient, Response
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, scrape_html
from slugify import slugify
from w3lib.html import get_base_url
from yt_dlp.extractor.generic import GenericIE

from mealie.core import exceptions
from mealie.core.config import get_app_settings
from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import safehttp
from mealie.schema.openai.general import OpenAIText
from mealie.schema.openai.recipe import OpenAIRecipe
from mealie.schema.recipe.recipe import Recipe, RecipeStep
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.services.openai import OpenAIService
from mealie.services.scraper.scraped_extras import ScrapedExtras

from . import cleaner

SCRAPER_TIMEOUT = 15

BROWSER_IMPERSONATIONS = [
    "chrome",
    "firefox",
    "safari",
    "edge",
]

logger = get_logger()


@functools.cache
def _get_yt_dlp_extractors() -> list:
    """Build and cache the yt-dlp extractor list once per process lifetime."""
    return [ie for ie in yt_dlp.extractor.gen_extractors() if ie.working() and not isinstance(ie, GenericIE)]


class ForceTimeoutException(Exception):
    pass


async def safe_scrape_html(url: str) -> str:
    """
    Scrapes the html from a url but will cancel the request
    if the request takes longer than SCRAPER_TIMEOUT seconds. This is used to mitigate
    DDOS attacks from users providing a url with arbitrary large content.

    Cycles through browser TLS impersonations (via httpx-curl-cffi) to bypass
    bot-detection systems that fingerprint the TLS handshake (JA3/JA4),
    such as Cloudflare.
    """
    logger.debug(f"Scraping URL: {url}")

    html_bytes = b""
    response: Response | None = None

    for impersonation in BROWSER_IMPERSONATIONS:
        logger.debug(f'Trying browser impersonation: "{impersonation}"')

        html_bytes = b""
        response = None

        transport = safehttp.AsyncSafeTransport(
            impersonate=impersonation,
            verify=False,  # disable SSL verification since we can handle untrusted data and some sites don't have certs
        )
        async with AsyncClient(transport=transport) as client:
            async with client.stream(
                "GET",
                url,
                timeout=SCRAPER_TIMEOUT,
                follow_redirects=True,
            ) as resp:
                if resp.status_code == 403:
                    logger.debug(f'403 Forbidden with impersonation "{impersonation}", trying next')
                    continue

                if resp.status_code >= 400:
                    logger.debug(f'Error status code {resp.status_code} with impersonation "{impersonation}"')
                    break

                start_time = time.time()

                async for chunk in resp.aiter_bytes(chunk_size=1024):
                    html_bytes += chunk

                    if time.time() - start_time > SCRAPER_TIMEOUT:
                        raise ForceTimeoutException()

                response = resp
                break

    if not (response and html_bytes):
        return ""

    # =====================================
    # Copied from requests text property

    # Try charset from content-type
    encoding = response.encoding

    # Fallback to auto-detected encoding.
    if encoding is None:
        encoding = response.apparent_encoding

    # Decode unicode from given encoding.
    try:
        content = str(html_bytes, encoding, errors="replace")
    except (LookupError, TypeError):
        # A LookupError is raised if the encoding was not found which could
        # indicate a misspelling or similar mistake.
        #
        # A TypeError can be raised if encoding is None
        #
        # So we try blindly encoding.
        content = str(html_bytes, errors="replace")

    return content


class ABCScraperStrategy(ABC):
    """
    Abstract class for all recipe parsers.
    """

    url: str

    def __init__(
        self,
        url: str,
        translator: Translator,
        raw_html: str | None = None,
    ) -> None:
        self.logger = get_logger()
        self.url = url
        self.raw_html = raw_html
        self.translator = translator

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


class RecipeScraperOpenAI(RecipeScraperPackage):
    """
    A wrapper around the `RecipeScraperPackage` class that uses OpenAI to extract the recipe from the URL,
    rather than trying to scrape it directly.
    """

    def can_scrape(self) -> bool:
        settings = get_app_settings()
        return settings.OPENAI_ENABLED and super().can_scrape()

    def extract_json_ld_data_from_html(self, soup: bs4.BeautifulSoup) -> str:
        data_parts: list[str] = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                script_data = script.string
                if script_data:
                    data_parts.append(str(script_data))
            except AttributeError:
                pass

        return "\n\n".join(data_parts)

    def find_image(self, soup: bs4.BeautifulSoup) -> str | None:
        # find the open graph image tag
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

        # find the largest image on the page
        largest_img = None
        max_size = 0
        for img in soup.find_all("img"):
            width = img.get("width", 0)
            height = img.get("height", 0)
            if not width or not height:
                continue

            try:
                size = int(width) * int(height)
            except (ValueError, TypeError):
                size = 1
            if size > max_size:
                max_size = size
                largest_img = img

        if largest_img:
            return largest_img.get("src")

        return None

    def format_html_to_text(self, html: str) -> str:
        soup = bs4.BeautifulSoup(html, "lxml")

        text = soup.get_text(separator="\n", strip=True)
        text += self.extract_json_ld_data_from_html(soup)
        if not text:
            raise Exception("No text or ld+json data found in HTML")

        try:
            image = self.find_image(soup)
        except Exception:
            image = None

        components = [f"Convert this content to JSON: {text}"]
        if image:
            components.append(f"Recipe Image: {image}")
        return "\n".join(components)

    async def get_html(self, url: str) -> str:
        settings = get_app_settings()
        if not settings.OPENAI_ENABLED:
            return ""

        html = self.raw_html or await safe_scrape_html(url)
        text = self.format_html_to_text(html)
        try:
            service = OpenAIService()
            prompt = service.get_prompt("recipes.scrape-recipe")

            response = await service.get_response(prompt, text, response_schema=OpenAIText)
            if not (response and response.text):
                raise Exception("OpenAI did not return any data")

            return self.ld_json_to_html(response.text)
        except Exception:
            self.logger.exception(f"OpenAI was unable to extract a recipe from {url}")
            return ""

    async def parse(self, on_progress: Callable[[str], Awaitable[None]] | None = None):
        if on_progress:
            await on_progress(self.translator.t("recipe.create-progress.creating-recipe-with-ai"))

        return await super().parse()


class TranscribedAudio(TypedDict):
    audio: Path
    subtitle: Path | None
    title: str
    description: str
    thumbnail_url: str | None
    transcription: str


class RecipeScraperOpenAITranscription(ABCScraperStrategy):
    SUBTITLE_LANGS = ["en", "fr", "es", "de", "it"]

    def can_scrape(self) -> bool:
        if not self.url:
            return False

        settings = get_app_settings()
        if not (settings.OPENAI_ENABLED and settings.OPENAI_ENABLE_TRANSCRIPTION_SERVICES):
            return False

        # Check if we can actually download something to transcribe
        return any(ie.suitable(self.url) for ie in _get_yt_dlp_extractors())

    @staticmethod
    def _parse_subtitle_content(subtitle_content: str) -> str:
        # TODO: is there a better way to parse subtitles that's more efficient?

        lines = []
        for line in subtitle_content.split("\n"):
            if line.strip() and not line.startswith("WEBVTT") and "-->" not in line and not line.isdigit():
                lines.append(line.strip())

        raw_content = " ".join(lines)
        content = re.sub(r"<[^>]+>", "", raw_content)
        return content

    def _download_audio(self, temp_path: Path) -> TranscribedAudio:
        """Downloads audio and subtitles from the video URL."""
        output_template = temp_path / "mealie"  # No extension here

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output_template) + ".%(ext)s",
            "quiet": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": self.SUBTITLE_LANGS,
            "skip_download": False,
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "32",
                }
            ],
            "postprocessor_args": ["-ac", "1"],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

                if info is None:
                    raise exceptions.VideoDownloadError(
                        "Failed to extract video information. The video may be unavailable or the URL is invalid."
                    )

                sub_path = None
                for lang in self.SUBTITLE_LANGS:
                    potential_path = output_template.with_suffix(f".{lang}.vtt")
                    if potential_path.exists():
                        sub_path = potential_path
                        break

                return {
                    "audio": output_template.with_suffix(".mp3"),
                    "subtitle": sub_path,
                    "title": info.get("title", ""),
                    "description": info.get("description", ""),
                    "thumbnail_url": info.get("thumbnail") or None,
                    "transcription": "",
                }
        except exceptions.VideoDownloadError:
            raise
        except Exception as e:
            raise exceptions.VideoDownloadError(f"Failed to download video: {e}") from e

    async def get_html(self, url: str) -> str:
        return self.raw_html or ""  # we don't use HTML with this scraper since we use ytdlp

    async def parse(
        self,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        openai_service = OpenAIService()

        with get_temporary_path() as temp_path:
            if on_progress:
                await on_progress(self.translator.t("recipe.create-progress.downloading-video"))

            video_data = await asyncio.to_thread(self._download_audio, temp_path)

            if video_data["subtitle"]:
                try:
                    with open(video_data["subtitle"], encoding="utf-8") as f:
                        subtitle_content = f.read()
                    video_data["transcription"] = self._parse_subtitle_content(subtitle_content)
                    self.logger.info("Using subtitles from video instead of transcription")
                except Exception:
                    self.logger.exception("Failed to read subtitles, falling back to transcription")
                    video_data["transcription"] = ""

            if not video_data["transcription"]:
                if on_progress:
                    await on_progress(self.translator.t("recipe.create-progress.transcribing-audio-with-ai"))

                try:
                    transcription = await openai_service.transcribe_audio(video_data["audio"])
                except exceptions.RateLimitError:
                    raise
                except Exception as e:
                    raise exceptions.OpenAIServiceError(f"Failed to transcribe audio: {e}") from e
                if not transcription:
                    raise exceptions.OpenAIServiceError("No transcription returned from OpenAI")
                video_data["transcription"] = transcription

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
