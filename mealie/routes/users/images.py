import shutil
from pathlib import Path

from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from pydantic import UUID4

from mealie.core.config import get_app_dirs
from mealie.core.dependencies import get_current_user
from mealie.core.dependencies.dependencies import temporary_dir
from mealie.routes.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import PrivateUser
from mealie.services.image import minify

public_router = APIRouter(prefix="", tags=["Users: Images"])
user_router = UserAPIRouter(prefix="", tags=["Users: Images"])


@public_router.get("/{id}/image")
async def get_user_image(id: str):
    """Returns a users profile picture"""
    app_dirs = get_app_dirs()

    user_dir = app_dirs.USER_DIR.joinpath(id)
    for recipe_image in user_dir.glob("profile_image.*"):
        return FileResponse(recipe_image)
    raise HTTPException(status.HTTP_404_NOT_FOUND)


@user_router.post("/{id}/image")
def update_user_image(
    id: UUID4,
    profile: UploadFile = File(...),
    temp_dir: Path = Depends(temporary_dir),
    current_user: PrivateUser = Depends(get_current_user),
):
    """Updates a User Image"""
    assert_user_change_allowed(id, current_user)

    temp_img = temp_dir.joinpath(profile.filename)

    with temp_img.open("wb") as buffer:
        shutil.copyfileobj(profile.file, buffer)

    image = minify.to_webp(temp_img)
    dest = PrivateUser.get_directory(id) / "profile.webp"

    shutil.copyfile(image, dest)

    if not dest.is_file:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
