import shutil

from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter

from mealie.core.config import get_app_dirs

app_dirs = get_app_dirs()
from mealie.core.dependencies import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import PrivateUser

public_router = APIRouter(prefix="", tags=["Users: Images"])
user_router = UserAPIRouter(prefix="", tags=["Users: Images"])


@public_router.get("/{id}/image")
async def get_user_image(id: str):
    """ Returns a users profile picture """
    user_dir = app_dirs.USER_DIR.joinpath(id)
    for recipe_image in user_dir.glob("profile_image.*"):
        return FileResponse(recipe_image)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@user_router.post("/{id}/image")
def update_user_image(
    id: str,
    profile_image: UploadFile = File(...),
    current_user: PrivateUser = Depends(get_current_user),
):
    """ Updates a User Image """

    assert_user_change_allowed(id, current_user)

    extension = profile_image.filename.split(".")[-1]

    app_dirs.USER_DIR.joinpath(id).mkdir(parents=True, exist_ok=True)

    [x.unlink() for x in app_dirs.USER_DIR.joinpath(id).glob("profile_image.*")]

    dest = app_dirs.USER_DIR.joinpath(id, f"profile_image.{extension}")

    with dest.open("wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    if not dest.is_file:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
