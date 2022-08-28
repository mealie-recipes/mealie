import asyncio
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from pydantic import UUID4

from mealie.pkgs import img
from mealie.schema.recipe.recipe import Recipe
from mealie.services._base_service import BaseService

_FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"


async def largest_content_len(urls: list[str]) -> tuple[str, int]:
    largest_url = ""
    largest_len = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(executor, lambda: session.head(url, headers={"User-Agent": _FIREFOX_UA}))
                for url in urls
            ]

            response: requests.Response  # required for type hinting within the loop
            for response in await asyncio.gather(*tasks):

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

    def __init__(self, recipe_id: UUID4, group_id: UUID4 = None) -> None:
        """
        RecipeDataService is a service that consolidates the reading/writing actions related
        to assets, and images for a recipe.
        """
        super().__init__()

        self.recipe_id = recipe_id
        self.slug = group_id
        self.minifier = img.PillowMinifier(purge=True, logger=self.logger)

        self.dir_data = Recipe.directory_from_id(self.recipe_id)
        self.dir_image = self.dir_data.joinpath("images")
        self.dir_assets = self.dir_data.joinpath("assets")

        self.dir_image.mkdir(parents=True, exist_ok=True)
        self.dir_assets.mkdir(parents=True, exist_ok=True)

    def delete_all_data(self) -> None:
        try:
            shutil.rmtree(self.dir_data)
        except Exception as e:
            self.logger.exception(f"Failed to delete recipe data: {e}")

    def write_image(self, file_data: bytes | Path, extension: str) -> Path:
        extension = extension.replace(".", "")
        image_path = self.dir_image.joinpath(f"original.{extension}")
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

    @staticmethod
    def _validate_image_url(url: str) -> bool:
        # sourcery skip: invert-any-all, use-any
        """
        Validates that the URL is of an allowed source and restricts certain sources to prevent
        malicious images from being downloaded.
        """
        invalid_domains = {"127.0.0.1", "localhost"}
        for domain in invalid_domains:
            if domain in url:
                return False

        return True

    def scrape_image(self, image_url) -> None:
        self.logger.debug(f"Image URL: {image_url}")

        if not self._validate_image_url(image_url):
            self.logger.error(f"Invalid image URL: {image_url}")
            raise InvalidDomainError(f"Invalid domain: {image_url}")

        if isinstance(image_url, str):  # Handles String Types
            pass

        elif isinstance(image_url, list):  # Handles List Types
            # Multiple images have been defined in the schema - usually different resolutions
            # Typically would be in smallest->biggest order, but can't be certain so test each.
            # 'Google will pick the best image to display in Search results based on the aspect ratio and resolution.'

            # TODO: We should refactor the scraper to use a async session provided by FastAPI using a sync
            # route instead of bootstrapping async behavior this far down the chain. Will require some work
            # so leaving this improvement here for now.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            future = asyncio.ensure_future(largest_content_len(image_url))
            loop.run_until_complete(future)
            image_url, _ = future.result()

        elif isinstance(image_url, dict):  # Handles Dictionary Types
            for key in image_url:
                if key == "url":
                    image_url = image_url.get("url")

        ext = image_url.split(".")[-1]

        if ext not in img.IMAGE_EXTENSIONS:
            ext = "jpg"  # Guess the extension

        file_name = f"{str(self.recipe_id)}.{ext}"
        file_path = Recipe.directory_from_id(self.recipe_id).joinpath("images", file_name)

        try:
            r = requests.get(image_url, stream=True, headers={"User-Agent": _FIREFOX_UA})
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

        r.raw.decode_content = True
        self.logger.info(f"File Name Suffix {file_path.suffix}")
        self.write_image(r.raw, file_path.suffix)

        file_path.unlink(missing_ok=True)
