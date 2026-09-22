import asyncio
import shutil
from logging import Logger
from pathlib import Path

from pydantic import UUID4

from mealie.pkgs import img, safehttp
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_image_types import RecipeImageTypes
from mealie.services._base_service import BaseService


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

    tasks = [safehttp.resilient_fetch(url, method="HEAD") for url in urls]
    responses: list[safehttp.FetchResult | None] = await gather_with_concurrency(
        max_concurrency, *tasks, ignore_exceptions=True
    )
    for response in responses:
        if response is None:
            continue

        len_int = int(response.headers.get("Content-Length", 0))
        if len_int > largest_len:
            largest_url = response.url
            largest_len = len_int

    return largest_url, largest_len


class NotAnImageError(Exception):
    pass


class InvalidDomainError(Exception):
    pass


class RecipeDataService(BaseService):
    minifier: img.ABCMinifier

    def __init__(self, recipe_id: UUID4, logger: Logger | None = None) -> None:
        """
        RecipeDataService is a service that consolidates the reading/writing actions related
        to assets, and images for a recipe.
        """
        super().__init__()

        self.recipe_id = recipe_id
        self.logger = logger or self.logger
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

        try:
            self.minifier.minify(image_path)
        except Exception:
            # Remove the partially-written file so corrupt images don't persist on disk.
            image_path.unlink(missing_ok=True)
            raise

        return image_path

    def delete_image(self, image_dir: Path | None = None):
        if not image_dir:
            image_dir = self.dir_image

        for img_type in RecipeImageTypes:
            image_path = image_dir.joinpath(img_type.value)
            image_path.unlink(missing_ok=True)

    async def fetch_image(self, image_url: str, max_bytes: int | None = None) -> tuple[bytes, str] | None:
        """Downloads the image at `image_url` and returns its bytes and file extension.

        The extension comes from the response's content type rather than the URL, which is
        often extensionless or buried under query parameters. Callers are responsible for
        deciding whether that extension is one they accept.

        Callers that store the bytes as-is should pass `max_bytes`, since the fetch is
        otherwise bounded only by time. Those that re-encode (see `scrape_image`) are already
        bounded by what the minifier writes out.

        Unlike `scrape_image`, nothing is written to disk, so the caller decides where the
        bytes belong. Returns `None` if nothing could be downloaded.
        """
        try:
            # FlareSolverr returns HTML, not image bytes, so it can't serve an image download.
            r = await safehttp.resilient_fetch(image_url, allow_flaresolverr=False, max_bytes=max_bytes)
        except safehttp.InvalidDomainError as e:
            # Re-raised as this module's error so callers only need one exception vocabulary.
            raise InvalidDomainError(str(e)) from e
        except safehttp.ResponseTooLargeError:
            # The caller set the budget, so it gets to report the overrun rather than seeing
            # it flattened into a generic failure.
            raise
        except Exception:
            self.logger.exception("Fatal Image Request Exception")
            return None

        if r is None:
            # Every impersonation was rejected, or the server returned an error status.
            return None

        content_type = r.headers.get("content-type", "").split(";")[0].strip().lower()

        if not content_type.startswith("image/"):
            self.logger.error(f"Content-Type: {content_type} is not an image")
            raise NotAnImageError(f"Content-Type {content_type} is not an image")

        # For the image types we care about the subtype is the extension ("image/png" -> "png").
        # Types where it isn't (e.g. "image/svg+xml") fall out of the caller's allowed set.
        return r.content, content_type.removeprefix("image/")

    async def scrape_image(self, image_url: str | dict[str, str] | list[str]) -> Path | None:
        """Downloads the image at `image_url` into the recipe's image directory.

        Returns the path the image was written to, or `None` if nothing could be
        downloaded. Callers must not record a cache key for a recipe unless a path
        comes back, or the recipe claims an image the media route cannot serve.
        """
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

        downloaded = await self.fetch_image(image_url_str)

        if downloaded is None:
            return None

        content, extension = downloaded

        # The extension only labels the bytes on their way into the minifier, which sniffs the
        # real format and converts everything to webp regardless.
        return self.write_image(content, extension)
