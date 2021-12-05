import shutil
from dataclasses import dataclass
from pathlib import Path

import requests

from mealie.core import root_logger
from mealie.schema.recipe import Recipe
from mealie.services.image import minify

logger = root_logger.get_logger()


@dataclass
class ImageOptions:
    ORIGINAL_IMAGE: str = "original.webp"
    MINIFIED_IMAGE: str = "min-original.webp"
    TINY_IMAGE: str = "tiny-original.webp"


IMG_OPTIONS = ImageOptions()


def write_image(recipe_slug: str, file_data: bytes, extension: str) -> Path:
    image_dir = Recipe(slug=recipe_slug).image_dir
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

    minify.minify_image(image_path, force=True)

    return image_path


def scrape_image(image_url: str, slug: str) -> Path:
    logger.info(f"Image URL: {image_url}")
    _FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"

    if isinstance(image_url, str):  # Handles String Types
        pass

    if isinstance(image_url, list):  # Handles List Types
        # Multiple images have been defined in the schema - usually different resolutions
        # Typically would be in smallest->biggest order, but can't be certain so test each.
        # 'Google will pick the best image to display in Search results based on the aspect ratio and resolution.'

        all_image_requests = []
        for url in image_url:
            if isinstance(url, dict):
                url = url.get("url", "")
            try:
                r = requests.get(url, stream=True, headers={"User-Agent": _FIREFOX_UA})
            except Exception:
                logger.exception("Image {url} could not be requested")
                continue
            if r.status_code == 200:
                all_image_requests.append((url, r))

        image_url, _ = max(all_image_requests, key=lambda url_r: len(url_r[1].content), default=("", 0))

    if isinstance(image_url, dict):  # Handles Dictionary Types
        for key in image_url:
            if key == "url":
                image_url = image_url.get("url")

    filename = slug + "." + image_url.split(".")[-1]
    filename = Recipe(slug=slug).image_dir.joinpath(filename)

    try:
        r = requests.get(image_url, stream=True, headers={"User-Agent": _FIREFOX_UA})
    except Exception:
        logger.exception("Fatal Image Request Exception")
        return None

    if r.status_code == 200:
        r.raw.decode_content = True
        logger.info(f"File Name Suffix {filename.suffix}")
        write_image(slug, r.raw, filename.suffix)

        filename.unlink(missing_ok=True)

        return Path(slug)

    return None
