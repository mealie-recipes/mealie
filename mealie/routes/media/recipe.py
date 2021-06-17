from enum import Enum

from fastapi import APIRouter, HTTPException, status
from mealie.schema.recipe import Recipe
from starlette.responses import FileResponse

"""
These routes are for development only! These assets are served by Caddy when not
in development mode. If you make changes, be sure to test the production container.
"""

router = APIRouter(prefix="/recipes")


class ImageType(str, Enum):
    original = "original.webp"
    small = "min-original.webp"
    tiny = "tiny-original.webp"


@router.get("/{recipe_slug}/images/{file_name}")
async def get_recipe_img(recipe_slug: str, file_name: ImageType = ImageType.original):
    """Takes in a recipe slug, returns the static image. This route is proxied in the docker image
    and should not hit the API in production"""
    recipe_image = Recipe(slug=recipe_slug).image_dir.joinpath(file_name.value)

    if recipe_image:
        return FileResponse(recipe_image)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@router.get("/{recipe_slug}/assets/{file_name}")
async def get_recipe_asset(recipe_slug: str, file_name: str):
    """ Returns a recipe asset """
    file = Recipe(slug=recipe_slug).asset_dir.joinpath(file_name)

    try:
        return FileResponse(file)
    except Exception:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
