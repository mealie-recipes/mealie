import shutil
from datetime import timedelta

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from mealie.core import security
from mealie.core.config import app_dirs, settings
from mealie.core.security import get_password_hash, verify_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.user import ChangePassword, UserBase, UserIn, UserInDB, UserOut
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    new_user: UserIn,
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    new_user.password = get_password_hash(new_user.password)

    return db.users.create(session, new_user.dict())


@router.get("", response_model=list[UserOut])
async def get_all_users(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    if not current_user.admin:
        raise HTTPException( status.HTTP_403_FORBIDDEN )
    
    return db.users.get_all(session)


@router.get("/self", response_model=UserOut)
async def get_logged_in_user(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    return current_user.dict()


@router.get("/{id}", response_model=UserOut)
async def get_user_by_id(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    return db.users.get(session, id)


@router.put("/{id}/reset-password")
async def reset_user_password(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    new_password = get_password_hash(settings.DEFAULT_PASSWORD)
    db.users.update_password(session, id, new_password)



@router.put("/{id}")
async def update_user(
    id: int,
    new_data: UserBase,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    token = None
    if current_user.id == id or current_user.admin:
        db.users.update(session, id, new_data.dict())
    if current_user.id == id:
        access_token = security.create_access_token(data=dict(sub=new_data.email))
        token = {"access_token": access_token, "token_type": "bearer"}
        return token


@router.get("/{id}/image")
async def get_user_image(id: str):
    """ Returns a users profile picture """
    user_dir = app_dirs.USER_DIR.joinpath(id)
    for recipe_image in user_dir.glob("profile_image.*"):
        return FileResponse(recipe_image)
    else:
        return False


@router.post("/{id}/image")
async def update_user_image(
    id: str,
    profile_image: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Updates a User Image """

    extension = profile_image.filename.split(".")[-1]

    app_dirs.USER_DIR.joinpath(id).mkdir(parents=True, exist_ok=True)

    try:
        [x.unlink() for x in app_dirs.USER_DIR.join(id).glob("profile_image.*")]
    except:
        pass

    dest = app_dirs.USER_DIR.joinpath(id, f"profile_image.{extension}")

    with dest.open("wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    if not dest.is_file:
        raise HTTPException( status.HTTP_500_INTERNAL_SERVER_ERROR )


@router.put("/{id}/password")
async def update_password(
    id: int,
    password_change: ChangePassword,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Resets the User Password"""

    match_passwords = verify_password(password_change.current_password, current_user.password)
    match_id = current_user.id == id

    if not ( match_passwords and match_id ):
        raise HTTPException( status.HTTP_401_UNAUTHORIZED )

    new_password = get_password_hash(password_change.new_password)
    db.users.update_password(session, id, new_password)
        


@router.delete("/{id}")
async def delete_user(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    if id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='SUPER_USER'
        )

    if current_user.id == id or current_user.admin:
        try:
            db.users.delete(session, id)
        except:
            raise HTTPException( status.HTTP_400_BAD_REQUEST )