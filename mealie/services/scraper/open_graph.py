from typing import Tuple

import extruct
from mealie.core.config import app_dirs
from slugify import slugify
from w3lib.html import get_base_url

LAST_JSON = app_dirs.DEBUG_DIR.joinpath("last_recipe.json")


def og_field(properties: dict, field_name: str) -> str:
    return next((val for name, val in properties if name == field_name), None)


def og_fields(properties: list[Tuple[str, str]], field_name: str) -> list[str]:
    return list({val for name, val in properties if name == field_name})


def basic_recipe_from_opengraph(html: str, url: str) -> dict:
    base_url = get_base_url(html, url)
    data = extruct.extract(html, base_url=base_url)
    try:
        properties = data["opengraph"][0]["properties"]
    except Exception:
        return

    return {
        "name": og_field(properties, "og:title"),
        "description": og_field(properties, "og:description"),
        "image": og_field(properties, "og:image"),
        "recipeYield": "",
        # FIXME: If recipeIngredient is an empty list, mongodb's data verification fails.
        "recipeIngredient": ["Could not detect ingredients"],
        # FIXME: recipeInstructions is allowed to be empty but message this is added for user sanity.
        "recipeInstructions": [{"text": "Could not detect instructions"}],
        "slug": slugify(og_field(properties, "og:title")),
        "orgURL": og_field(properties, "og:url"),
        "categories": [],
        "tags": og_fields(properties, "og:article:tag"),
        "dateAdded": None,
        "notes": [],
        "extras": [],
    }
