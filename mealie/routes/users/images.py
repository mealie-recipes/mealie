import shutil
from pathlib import Path

from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.routing import APIRouter
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie import utils
from mealie.core.dependencies import get_current_user
from mealie.core.dependencies.dependencies import temporary_dir
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import PrivateUser
from mealie.services.image import minify

public_router = APIRouter(prefix="", tags=["Users: Images"])
user_router = UserAPIRouter(prefix="", tags=["Users: Images"])


@user_router.post("/{id}/image")
def update_user_image(
    id: UUID4,
    profile: UploadFile = File(...),
    temp_dir: Path = Depends(temporary_dir),
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """Updates a User Image"""
    assert_user_change_allowed(id, current_user)

    temp_img = temp_dir.joinpath(profile.filename)

    with temp_img.open("wb") as buffer:
        shutil.copyfileobj(profile.file, buffer)

    image = minify.to_webp(temp_img)
    dest = PrivateUser.get_directory(id) / "profile.webp"

    shutil.copyfile(image, dest)

    db = get_repositories(session)

    db.users.patch(id, {"cache_key": utils.new_cache_key()})

    if not dest.is_file:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
