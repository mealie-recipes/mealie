from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.schema.user import PrivateUser

router = APIRouter(prefix="/users")

# the frontend busts this with a `?cacheKey=<user.cacheKey>` query param on re-upload
# (see frontend/app/components/Domain/User/UserAvatar.vue), so the response at a given
# URL never changes and can be cached indefinitely
IMMUTABLE_IMAGE_HEADERS = {"Cache-Control": "public, max-age=31536000, immutable"}


@router.get("/{user_id}/{file_name}", response_class=FileResponse)
async def get_user_image(user_id: UUID4, file_name: str):
    """Takes in a recipe slug, returns the static image. This route is proxied in the docker image
    and should not hit the API in production"""
    user_dir = PrivateUser.get_directory(user_id)
    recipe_image = (user_dir / file_name).resolve()

    if not recipe_image.is_relative_to(user_dir.resolve()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if recipe_image.exists():
        return FileResponse(recipe_image, media_type="image/webp", headers=IMMUTABLE_IMAGE_HEADERS)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
