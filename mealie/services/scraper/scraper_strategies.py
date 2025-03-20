import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import bs4
import extruct
from fastapi import HTTPException, status
from httpx import AsyncClient, Response
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, scrape_html
from slugify import slugify
from w3lib.html import get_base_url

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.pkgs import safehttp
from mealie.schema.recipe.recipe import Recipe, RecipeStep
from mealie.services.openai import OpenAIService
from mealie.services.scraper.scraped_extras import ScrapedExtras

from . import cleaner
from .user_agents_manager import get_user_agents_manager

SCRAPER_TIMEOUT = 15
logger = get_logger()


class ForceTimeoutException(Exception):
    pass


async def safe_scrape_html(url: str) -> str:
    """
    Scrapes the html from a url but will cancel the request
    if the request takes longer than 15 seconds. This is used to mitigate
    DDOS attacks from users providing a url with arbitrary large content.
    """
    user_agents_manager = get_user_agents_manager()

    logger.debug(f"Scraping URL: {url}")
    async with AsyncClient(transport=safehttp.AsyncSafeTransport()) as client:
        for user_agent in user_agents_manager.user_agents:
            logger.debug(f'Trying User-Agent: "{user_agent}"')

            response: Response | None = None
            html_bytes = b""
            async with client.stream(
                "GET",
                url,
                timeout=SCRAPER_TIMEOUT,
                headers=user_agents_manager.get_scrape_headers(user_agent),
                follow_redirects=True,
            ) as resp:
                if resp.status_code == status.HTTP_403_FORBIDDEN:
                    logger.debug(f'403 Forbidden with User-Agent: "{user_agent}"')
                    continue

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
        content = None
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
    async def get_html(self, url: str) -> str: ...

    @abstractmethod
    async def parse(self) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        """Parse a recipe from a web URL.

        Args:
            recipe_url (str): Full URL of the recipe to scrape.

        Returns:
            Recipe: Recipe object.
        """
        ...


class RecipeScraperPackage(ABCScraperStrategy):
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

        cook_time = try_get_default(
            None, "performTime", None, cleaner.clean_time, translator=self.translator
        ) or try_get_default(scraped_data.cook_time, "cookTime", None, cleaner.clean_time, translator=self.translator)

        extras = ScrapedExtras()

        extras.set_tags(try_get_default(scraped_data.keywords, "keywords", "", cleaner.clean_tags))

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

    async def parse(self):
        """
        Parse a recipe from a given url.
        """
        scraped_data = await self.scrape_url()

        if scraped_data is None:
            return None

        return self.clean_scraper(scraped_data, self.url)


class RecipeScraperOpenAI(RecipeScraperPackage):
    """
    A wrapper around the `RecipeScraperPackage` class that uses OpenAI to extract the recipe from the URL,
    rather than trying to scrape it directly.
    """

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

            response_json = await service.get_response(prompt, text, force_json_response=True)
            if not response_json:
                raise Exception("OpenAI did not return any data")

            return self.ld_json_to_html(response_json)
        except Exception:
            self.logger.exception(f"OpenAI was unable to extract a recipe from {url}")
            return ""


class RecipeScraperOpenGraph(ABCScraperStrategy):
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

    async def parse(self):
        """
        Parse a recipe from a given url.
        """
        html = await self.get_html(self.url)

        og_data = self.get_recipe_fields(html)

        if og_data is None:
            return None

        return Recipe(**og_data), ScrapedExtras()
