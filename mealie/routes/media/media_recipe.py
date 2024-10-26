from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventOut

router = APIRouter(prefix="/recipes")


class ImageType(str, Enum):
    original = "original.webp"
    small = "min-original.webp"
    tiny = "tiny-original.webp"


@router.get("/{recipe_id}/images/{file_name}")
async def get_recipe_img(recipe_id: str, file_name: ImageType = ImageType.original):
    """
    Takes in a recipe id, returns the static image. This route is proxied in the docker image
    and should not hit the API in production
    """
    recipe_image = Recipe.directory_from_id(recipe_id).joinpath("images", file_name.value)

    if recipe_image.exists():
        return FileResponse(recipe_image, media_type="image/webp")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@router.get("/{recipe_id}/images/timeline/{timeline_event_id}/{file_name}")
async def get_recipe_timeline_event_img(
    recipe_id: str, timeline_event_id: str, file_name: ImageType = ImageType.original
):
    """
    Takes in a recipe id and event timeline id, returns the static image. This route is proxied in the docker image
    and should not hit the API in production
    """
    timeline_event_image = RecipeTimelineEventOut.image_dir_from_id(recipe_id, timeline_event_id).joinpath(
        file_name.value
    )

    if timeline_event_image.exists():
        return FileResponse(timeline_event_image, media_type="image/webp")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@router.get("/{recipe_id}/assets/{file_name}")
async def get_recipe_asset(recipe_id: UUID4, file_name: str):
    """Returns a recipe asset"""
    file = Recipe.directory_from_id(recipe_id).joinpath("assets", file_name)

    try:
        return FileResponse(file)
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND) from e
