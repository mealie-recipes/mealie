import shutil
from datetime import timedelta
from os import access

from mealie.core.config import USER_DIR
from mealie.core.security import get_password_hash, verify_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from mealie.routes.deps import manager
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import ChangePassword, UserBase, UserIn, UserInDB, UserOut
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    new_user: UserIn,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):

    new_user.password = get_password_hash(new_user.password)

    data = db.users.create(session, new_user.dict())
    return SnackResponse.success(f"User Created: {new_user.full_name}", data)


@router.get("", response_model=list[UserOut])
async def get_all_users(
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):

    if current_user.admin:
        return db.users.get_all(session)
    else:
        return {"details": "user not authorized"}


@router.get("/self", response_model=UserOut)
async def get_logged_in_user(
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    return current_user.dict()


@router.get("/{id}", response_model=UserOut)
async def get_user_by_id(
    id: int,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    return db.users.get(session, id)


@router.put("/{id}")
async def update_user(
    id: int,
    new_data: UserBase,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):

    access_token = None
    if current_user.id == id or current_user.admin:
        updated_user: UserInDB = db.users.update(session, id, new_data.dict())
        email = updated_user.email
        if current_user.id == id:
            access_token = manager.create_access_token(data=dict(sub=email), expires=timedelta(hours=2))
            access_token = {"access_token": access_token, "token_type": "bearer"}

    return SnackResponse.success("User Updated", access_token)


@router.get("/{id}/image")
async def get_user_image(id: str):
    """ Returns a users profile picture """
    user_dir = USER_DIR.joinpath(id)
    for recipe_image in user_dir.glob("profile_image.*"):
        return FileResponse(recipe_image)
    else:
        return False


@router.post("/{id}/image")
async def update_user_image(
    id: str,
    profile_image: UploadFile = File(...),
    current_user: UserInDB = Depends(manager),
):
    """ Updates a User Image """

    extension = profile_image.filename.split(".")[-1]

    USER_DIR.joinpath(id).mkdir(parents=True, exist_ok=True)

    try:
        [x.unlink() for x in USER_DIR.join(id).glob("profile_image.*")]
    except:
        pass

    dest = USER_DIR.joinpath(id, f"profile_image.{extension}")

    with dest.open("wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    if dest.is_file:
        return SnackResponse.success("Backup uploaded")
    else:
        return SnackResponse.error("Failure uploading file")


@router.put("/{id}/password")
async def update_password(
    id: int,
    password_change: ChangePassword,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Resets the User Password"""

    match_passwords = verify_password(password_change.current_password, current_user.password)
    match_id = current_user.id == id

    if match_passwords and match_id:
        new_password = get_password_hash(password_change.new_password)
        db.users.update_password(session, id, new_password)
        return SnackResponse.success("Password Updated")
    else:
        return SnackResponse.error("Existing password does not match")


@router.delete("/{id}")
async def delete_user(
    id: int,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    if id == 1:
        return SnackResponse.error("Error! Cannot Delete Super User")

    if current_user.id == id or current_user.admin:
        db.users.delete(session, id)
        return SnackResponse.error(f"User Deleted")
