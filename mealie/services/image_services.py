import shutil
from dataclasses import dataclass
from pathlib import Path

import requests
from fastapi.logger import logger
from mealie.core.config import app_dirs


@dataclass
class ImageOptions:
    ORIGINAL_IMAGE: str = "original*"
    MINIFIED_IMAGE: str = "min-original*"
    TINY_IMAGE: str = "tiny-original*"


IMG_OPTIONS = ImageOptions()


def read_image(recipe_slug: str, image_type: str = "original") -> Path:
    """returns the path to the image file for the recipe base of image_type

    Args:
        recipe_slug (str): Recipe Slug
        image_type (str, optional): Glob Style Matcher "original*" | "min-original* | "tiny-original*"

    Returns:
        Path: [description]
    """
    recipe_slug = recipe_slug.split(".")[0]  # Incase of File Name
    recipe_image_dir = app_dirs.IMG_DIR.joinpath(recipe_slug)

    glob_string = "original*" if image_type else "min-original*"

    for file in recipe_image_dir.glob(glob_string):
        return file

    return None


def write_image(recipe_slug: str, file_data: bytes, extension: str) -> Path.name:
    delete_image(recipe_slug)

    image_path = Path(app_dirs.IMG_DIR.joinpath(f"{recipe_slug}.{extension}"))
    with open(image_path, "ab") as f:
        f.write(file_data)

    return image_path


def delete_image(recipe_slug: str) -> str:
    recipe_slug = recipe_slug.split(".")[0]
    for file in app_dirs.IMG_DIR.glob(f"{recipe_slug}*"):
        return file.unlink()


def scrape_image(image_url: str, slug: str) -> Path:
    if isinstance(image_url, str):  # Handles String Types
        image_url = image_url

    if isinstance(image_url, list):  # Handles List Types
        image_url = image_url[0]

    if isinstance(image_url, dict):  # Handles Dictionary Types
        for key in image_url:
            if key == "url":
                image_url = image_url.get("url")

    filename = slug + "." + image_url.split(".")[-1]
    filename = app_dirs.IMG_DIR.joinpath(filename)

    try:
        r = requests.get(image_url, stream=True)
    except:
        logger.exception("Fatal Image Request Exception")
        return None

    if r.status_code == 200:
        r.raw.decode_content = True

        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        return filename

    return None
