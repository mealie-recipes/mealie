import shutil

from fastapi import (BackgroundTasks, Depends, File, HTTPException, UploadFile,
                     status)
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from mealie.core import security
from mealie.core.config import app_dirs, settings
from mealie.core.security import get_password_hash, verify_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.schema.user import (ChangePassword, UserBase, UserFavorites,
                                UserIn, UserInDB, UserOut)
from mealie.services.events import create_user_event
from sqlalchemy.orm.session import Session

public_router = APIRouter(prefix="/api/users", tags=["Users"])
user_router = UserAPIRouter(prefix="/api/users", tags=["Users"])
admin_router = AdminAPIRouter(prefix="/api/users", tags=["Users"])


async def assert_user_change_allowed(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
):
    if current_user.id != id and not current_user.admin:
        # only admins can edit other users
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="NOT_AN_ADMIN")


@admin_router.post("", response_model=UserOut, status_code=201)
async def create_user(
    background_tasks: BackgroundTasks,
    new_user: UserIn,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    new_user.password = get_password_hash(new_user.password)
    background_tasks.add_task(
        create_user_event, "User Created", f"Created by {current_user.full_name}", session=session
    )
    return db.users.create(session, new_user.dict())


@admin_router.get("", response_model=list[UserOut])
async def get_all_users(session: Session = Depends(generate_session)):
    return db.users.get_all(session)


@user_router.get("/self", response_model=UserOut)
async def get_logged_in_user(
    current_user: UserInDB = Depends(get_current_user),
):
    return current_user.dict()


@admin_router.get("/{id}", response_model=UserOut)
async def get_user_by_id(
    id: int,
    session: Session = Depends(generate_session),
):
    return db.users.get(session, id)


@user_router.put("/{id}/reset-password")
async def reset_user_password(
    id: int,
    session: Session = Depends(generate_session),
):

    new_password = get_password_hash(settings.DEFAULT_PASSWORD)
    db.users.update_password(session, id, new_password)


@user_router.put("/{id}")
async def update_user(
    id: int,
    new_data: UserBase,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    assert_user_change_allowed(id)

    if not current_user.admin and (new_data.admin or current_user.group != new_data.group):
        # prevent a regular user from doing admin tasks on themself
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if current_user.id == id and current_user.admin and not new_data.admin:
        # prevent an admin from demoting themself
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    db.users.update(session, id, new_data.dict())
    if current_user.id == id:
        access_token = security.create_access_token(data=dict(sub=new_data.email))
        token = {"access_token": access_token, "token_type": "bearer"}
        return token


@public_router.get("/{id}/image")
async def get_user_image(id: str):
    """ Returns a users profile picture """
    user_dir = app_dirs.USER_DIR.joinpath(id)
    for recipe_image in user_dir.glob("profile_image.*"):
        return FileResponse(recipe_image)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@user_router.post("/{id}/image")
async def update_user_image(
    id: str,
    profile_image: UploadFile = File(...),
):
    """ Updates a User Image """

    assert_user_change_allowed(id)

    extension = profile_image.filename.split(".")[-1]

    app_dirs.USER_DIR.joinpath(id).mkdir(parents=True, exist_ok=True)

    [x.unlink() for x in app_dirs.USER_DIR.joinpath(id).glob("profile_image.*")]

    dest = app_dirs.USER_DIR.joinpath(id, f"profile_image.{extension}")

    with dest.open("wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    if not dest.is_file:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_router.put("/{id}/password")
async def update_password(
    id: int,
    password_change: ChangePassword,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Resets the User Password"""

    assert_user_change_allowed(id)
    match_passwords = verify_password(password_change.current_password, current_user.password)
    match_id = current_user.id == id

    if not (match_passwords and match_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    new_password = get_password_hash(password_change.new_password)
    db.users.update_password(session, id, new_password)


@user_router.get("/{id}/favorites", response_model=UserFavorites)
async def get_favorites(id: str, session: Session = Depends(generate_session)):
    """ Get user's favorite recipes """

    return db.users.get(session, id, override_schema=UserFavorites)


@user_router.post("/{id}/favorites/{slug}")
async def add_favorite(
    slug: str,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Adds a Recipe to the users favorites """

    current_user.favorite_recipes.append(slug)

    db.users.update(session, current_user.id, current_user)


@user_router.delete("/{id}/favorites/{slug}")
async def remove_favorite(
    slug: str,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Adds a Recipe to the users favorites """

    current_user.favorite_recipes = [x for x in current_user.favorite_recipes if x != slug]

    db.users.update(session, current_user.id, current_user)

    return


@admin_router.delete("/{id}")
async def delete_user(
    background_tasks: BackgroundTasks,
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    assert_user_change_allowed(id)

    if id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SUPER_USER")

    if current_user.id == id or current_user.admin:
        try:
            db.users.delete(session, id)
            background_tasks.add_task(create_user_event, "User Deleted", f"User ID: {id}", session=session)
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
