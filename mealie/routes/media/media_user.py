from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.schema.user import PrivateUser

"""
These routes are for development only! These assets are served by Caddy when not
in development mode. If you make changes, be sure to test the production container.
"""

router = APIRouter(prefix="/users")


@router.get("/{user_id}/{file_name}", response_class=FileResponse)
async def get_user_image(user_id: UUID4, file_name: str):
    """Takes in a recipe slug, returns the static image. This route is proxied in the docker image
    and should not hit the API in production"""
    recipe_image = PrivateUser.get_directory(user_id) / file_name

    if recipe_image.exists():
        return FileResponse(recipe_image, media_type="image/webp")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
