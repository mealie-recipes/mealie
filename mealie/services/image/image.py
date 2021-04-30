import shutil
from dataclasses import dataclass
from pathlib import Path

import requests
from mealie.core import root_logger
from mealie.core.config import app_dirs
from mealie.services.image import minify

logger = root_logger.get_logger()


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

    for file in recipe_image_dir.glob(image_type):
        return file

    return None


def rename_image(original_slug, new_slug) -> Path:
    current_path = app_dirs.IMG_DIR.joinpath(original_slug)
    new_path = app_dirs.IMG_DIR.joinpath(new_slug)

    try:
        new_path = current_path.rename(new_path)
    except FileNotFoundError:
        logger.error(f"Image Directory {original_slug} Doesn't Exist")

    return new_path


def write_image(recipe_slug: str, file_data: bytes, extension: str) -> Path:
    try:
        delete_image(recipe_slug)
    except Exception:
        pass

    image_dir = Path(app_dirs.IMG_DIR.joinpath(f"{recipe_slug}"))
    image_dir.mkdir(exist_ok=True, parents=True)
    extension = extension.replace(".", "")
    image_path = image_dir.joinpath(f"original.{extension}")

    if isinstance(file_data, Path):
        shutil.copy2(file_data, image_path)
    elif isinstance(file_data, bytes):
        with open(image_path, "ab") as f:
            f.write(file_data)
    else:
        with open(image_path, "ab") as f:
            shutil.copyfileobj(file_data, f)

    print(image_path)
    minify.minify_image(image_path)

    return image_path


def delete_image(recipe_slug: str) -> str:
    recipe_slug = recipe_slug.split(".")[0]
    for file in app_dirs.IMG_DIR.glob(f"{recipe_slug}*"):
        return shutil.rmtree(file)


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
    except Exception:
        logger.exception("Fatal Image Request Exception")
        return None

    if r.status_code == 200:
        r.raw.decode_content = True

        write_image(slug, r.raw, filename.suffix)

        filename.unlink(missing_ok=True)

        return slug

    return None
