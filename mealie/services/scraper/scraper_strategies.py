import time
from abc import ABC, abstractmethod
from typing import Any, Callable

import extruct
import requests
from fastapi import HTTPException, status
from recipe_scrapers import NoSchemaFoundInWildMode, SchemaScraperFactory, scrape_html
from slugify import slugify
from w3lib.html import get_base_url

from mealie.core.root_logger import get_logger
from mealie.schema.recipe.recipe import Recipe, RecipeStep
from mealie.services.scraper.scraped_extras import ScrapedExtras

from . import cleaner

_FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
SCRAPER_TIMEOUT = 15


class ForceTimeoutException(Exception):
    pass


def safe_scrape_html(url: str) -> str:
    """
    Scrapes the html from a url but will cancel the request
    if the request takes longer than 15 seconds. This is used to mitigate
    DDOS attacks from users providing a url with arbitrary large content.
    """
    resp = requests.get(url, timeout=SCRAPER_TIMEOUT, stream=True, headers={"User-Agent": _FIREFOX_UA})

    html_bytes = b""

    start_time = time.time()

    for chunk in resp.iter_content(chunk_size=1024):
        html_bytes += chunk

        if time.time() - start_time > SCRAPER_TIMEOUT:
            raise ForceTimeoutException()

    # =====================================
    # Copied from requests text property

    # Try charset from content-type
    content = None
    encoding = resp.encoding

    if not html_bytes:
        return ""

    # Fallback to auto-detected encoding.
    if encoding is None:
        encoding = resp.apparent_encoding

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

    def __init__(self, url: str) -> None:
        self.logger = get_logger()
        self.url = url

    @abstractmethod
    def parse(self) -> tuple[Recipe, ScrapedExtras] | tuple[None, None]:
        """Parse a recipe from a web URL.

        Args:
            recipe_url (str): Full URL of the recipe to scrape.

        Returns:
            Recipe: Recipe object.
        """
        ...


class RecipeScraperPackage(ABCScraperStrategy):
    def clean_scraper(self, scraped_data: SchemaScraperFactory.SchemaScraper, url: str) -> tuple[Recipe, ScrapedExtras]:
        def try_get_default(func_call: Callable | None, get_attr: str, default: Any, clean_func=None):
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
                value = clean_func(value)

            return value

        def get_instructions() -> list[RecipeStep]:
            instruction_as_text = try_get_default(
                scraped_data.instructions, "recipeInstructions", ["No Instructions Found"]
            )

            self.logger.debug(f"Scraped Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

            instruction_as_text = cleaner.clean_instructions(instruction_as_text)

            self.logger.debug(f"Cleaned Instructions: (Type: {type(instruction_as_text)}) \n {instruction_as_text}")

            try:
                return [RecipeStep(title="", text=x.get("text")) for x in instruction_as_text]
            except TypeError:
                return []

        cook_time = try_get_default(None, "performTime", None, cleaner.clean_time) or try_get_default(
            None, "cookTime", None, cleaner.clean_time
        )

        extras = ScrapedExtras()

        extras.set_tags(try_get_default(None, "keywords", "", cleaner.clean_tags))

        recipe = Recipe(
            name=try_get_default(scraped_data.title, "name", "No Name Found", cleaner.clean_string),
            slug="",
            image=try_get_default(None, "image", None),
            description=try_get_default(None, "description", "", cleaner.clean_string),
            nutrition=try_get_default(None, "nutrition", None, cleaner.clean_nutrition),
            recipe_yield=try_get_default(scraped_data.yields, "recipeYield", "1", cleaner.clean_string),
            recipe_ingredient=try_get_default(
                scraped_data.ingredients, "recipeIngredient", [""], cleaner.clean_ingredients
            ),
            recipe_instructions=get_instructions(),
            total_time=try_get_default(None, "totalTime", None, cleaner.clean_time),
            prep_time=try_get_default(None, "prepTime", None, cleaner.clean_time),
            perform_time=cook_time,
            org_url=url,
        )

        return recipe, extras

    def scrape_url(self) -> SchemaScraperFactory.SchemaScraper | Any | None:
        recipe_html = safe_scrape_html(self.url)

        try:
            scraped_schema = scrape_html(recipe_html, org_url=self.url)
        except (NoSchemaFoundInWildMode, AttributeError):
            self.logger.error("Recipe Scraper was unable to extract a recipe.")
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

    def parse(self):
        """
        Parse a recipe from a given url.
        """
        scraped_data = self.scrape_url()

        if scraped_data is None:
            return None

        return self.clean_scraper(scraped_data, self.url)


class RecipeScraperOpenGraph(ABCScraperStrategy):
    """
    Abstract class for all recipe parsers.
    """

    def get_html(self) -> str:
        return safe_scrape_html(self.url)

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
            "orgURL": og_field(properties, "og:url"),
            "categories": [],
            "tags": og_fields(properties, "og:article:tag"),
            "dateAdded": None,
            "notes": [],
            "extras": [],
        }

    def parse(self):
        """
        Parse a recipe from a given url.
        """
        html = self.get_html()

        og_data = self.get_recipe_fields(html)

        if og_data is None:
            return None

        return Recipe(**og_data), ScrapedExtras()
