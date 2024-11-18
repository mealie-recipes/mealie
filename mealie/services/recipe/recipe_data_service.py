import asyncio
import shutil
from pathlib import Path

from httpx import AsyncClient, Response
from pydantic import UUID4

from mealie.pkgs import img, safehttp
from mealie.pkgs.safehttp.transport import AsyncSafeTransport
from mealie.schema.recipe.recipe import Recipe
from mealie.services._base_service import BaseService

try:
    from recipe_scrapers._abstract import HEADERS

    _FIREFOX_UA = HEADERS["User-Agent"]
except (ImportError, KeyError):
    _FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/128.0"


async def gather_with_concurrency(n, *coros, ignore_exceptions=False):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    results = await asyncio.gather(*(sem_coro(c) for c in coros), return_exceptions=ignore_exceptions)
    if ignore_exceptions:
        results = [r for r in results if not isinstance(r, Exception)]
    return results


async def largest_content_len(urls: list[str]) -> tuple[str, int]:
    largest_url = ""
    largest_len = 0

    max_concurrency = 10

    async def do(client: AsyncClient, url: str) -> Response:
        return await client.head(url, headers={"User-Agent": _FIREFOX_UA})

    async with AsyncClient(transport=safehttp.AsyncSafeTransport()) as client:
        tasks = [do(client, url) for url in urls]
        responses: list[Response] = await gather_with_concurrency(max_concurrency, *tasks, ignore_exceptions=True)
        for response in responses:
            len_int = int(response.headers.get("Content-Length", 0))
            if len_int > largest_len:
                largest_url = str(response.url)
                largest_len = len_int

    return largest_url, largest_len


class NotAnImageError(Exception):
    pass


class InvalidDomainError(Exception):
    pass


class RecipeDataService(BaseService):
    minifier: img.ABCMinifier

    def __init__(self, recipe_id: UUID4) -> None:
        """
        RecipeDataService is a service that consolidates the reading/writing actions related
        to assets, and images for a recipe.
        """
        super().__init__()

        self.recipe_id = recipe_id
        self.minifier = img.PillowMinifier(purge=True, logger=self.logger)

        self.dir_data = Recipe.directory_from_id(self.recipe_id)
        self.dir_image = self.dir_data.joinpath("images")
        self.dir_image_timeline = self.dir_image.joinpath("timeline")
        self.dir_assets = self.dir_data.joinpath("assets")

        for dir in [self.dir_image, self.dir_image_timeline, self.dir_assets]:
            dir.mkdir(parents=True, exist_ok=True)

    def delete_all_data(self) -> None:
        try:
            shutil.rmtree(self.dir_data)
        except Exception as e:
            self.logger.exception(f"Failed to delete recipe data: {e}")

    def write_image(self, file_data: bytes | Path, extension: str, image_dir: Path | None = None) -> Path:
        if not image_dir:
            image_dir = self.dir_image

        extension = extension.replace(".", "")
        image_path = image_dir.joinpath(f"original.{extension}")
        image_path.unlink(missing_ok=True)

        if isinstance(file_data, Path):
            shutil.copy2(file_data, image_path)
        elif isinstance(file_data, bytes):
            with open(image_path, "ab") as f:
                f.write(file_data)
        else:
            with open(image_path, "ab") as f:
                shutil.copyfileobj(file_data, f)

        self.minifier.minify(image_path)

        return image_path

    async def scrape_image(self, image_url: str | dict[str, str] | list[str]) -> None:
        self.logger.info(f"Image URL: {image_url}")

        image_url_str = ""

        if isinstance(image_url, str):  # Handles String Types
            image_url_str = image_url

        elif isinstance(image_url, list):  # Handles List Types
            # Multiple images have been defined in the schema - usually different resolutions
            # Typically would be in smallest->biggest order, but can't be certain so test each.
            # 'Google will pick the best image to display in Search results based on the aspect ratio and resolution.'
            image_url_str, _ = await largest_content_len(image_url)

        elif isinstance(image_url, dict):  # Handles Dictionary Types
            for key in image_url:
                if key == "url":
                    image_url_str = image_url.get("url", "")

        if not image_url_str:
            raise ValueError(f"image url could not be parsed from input: {image_url}")

        ext = image_url_str.split(".")[-1]

        if ext not in img.IMAGE_EXTENSIONS:
            ext = "jpg"  # Guess the extension

        file_name = f"{self.recipe_id!s}.{ext}"
        file_path = Recipe.directory_from_id(self.recipe_id).joinpath("images", file_name)

        async with AsyncClient(transport=AsyncSafeTransport()) as client:
            try:
                r = await client.get(image_url_str, headers={"User-Agent": _FIREFOX_UA})
            except Exception:
                self.logger.exception("Fatal Image Request Exception")
                return None

            if r.status_code != 200:
                # TODO: Probably should throw an exception in this case as well, but before these changes
                # we were returning None if it failed anyways.
                return None

            content_type = r.headers.get("content-type", "")

            if "image" not in content_type:
                self.logger.error(f"Content-Type: {content_type} is not an image")
                raise NotAnImageError(f"Content-Type {content_type} is not an image")

            self.logger.debug(f"File Name Suffix {file_path.suffix}")
            self.write_image(r.read(), file_path.suffix)
            file_path.unlink(missing_ok=True)
