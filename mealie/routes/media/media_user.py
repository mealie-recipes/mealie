from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.schema.user import PrivateUser

router = APIRouter(prefix="/users")


@router.get("/{user_id}/{file_name}", response_class=FileResponse)
async def get_user_image(user_id: UUID4, file_name: str):
    """Takes in a recipe slug, returns the static image. This route is proxied in the docker image
    and should not hit the API in production"""
    user_dir = PrivateUser.get_directory(user_id)
    recipe_image = (user_dir / file_name).resolve()

    if not recipe_image.is_relative_to(user_dir.resolve()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if recipe_image.exists():
        return FileResponse(recipe_image, media_type="image/webp")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
