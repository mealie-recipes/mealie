from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm.session import Session

from mealie.core.config import app_dirs, settings
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.schema.user import LongLiveTokenInDB, PrivateUser, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
oauth2_scheme_soft_fail = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)
ALGORITHM = "HS256"


async def is_logged_in(token: str = Depends(oauth2_scheme_soft_fail), session=Depends(generate_session)) -> bool:
    """
    When you need to determine if the user is logged in, but don't need the user, you can use this
    function to return a boolean value to represent if the user is logged in. No Auth exceptions are raised
    if the user is not logged in. This behavior is not the same as 'get_current_user'

    Args:
        token (str, optional): [description]. Defaults to Depends(oauth2_scheme_soft_fail).
        session ([type], optional): [description]. Defaults to Depends(generate_session).

    Returns:
        bool: True = Valid User / False = Not User
    """
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        long_token: str = payload.get("long_token")

        if long_token is not None:
            try:
                user = validate_long_live_token(session, token, payload.get("id"))
                if user:
                    return True
            except Exception:
                return False

        return username is not None

    except Exception:
        return False


async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(generate_session)) -> PrivateUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        long_token: str = payload.get("long_token")

        if long_token is not None:
            return validate_long_live_token(session, token, payload.get("id"))

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    db = get_database(session)

    user = db.users.get(token_data.username, "email", any_case=True)
    if user is None:
        raise credentials_exception
    return user


async def get_admin_user(current_user=Depends(get_current_user)) -> PrivateUser:
    if not current_user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return current_user


def validate_long_live_token(session: Session, client_token: str, id: int) -> PrivateUser:
    db = get_database(session)

    tokens: list[LongLiveTokenInDB] = db.api_tokens.get( id, "parent_id", limit=9999)

    for token in tokens:
        token: LongLiveTokenInDB
        if token.token == client_token:
            return token.user


def validate_file_token(token: Optional[str] = None) -> Path:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate file token",
    )
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
        file_path = Path(payload.get("file"))
    except JWTError:
        raise credentials_exception

    return file_path


async def temporary_zip_path() -> Path:
    temp_path = app_dirs.TEMP_DIR.mkdir(exist_ok=True, parents=True)
    temp_path = app_dirs.TEMP_DIR.joinpath("my_zip_archive.zip")

    try:
        yield temp_path
    finally:
        temp_path.unlink(missing_ok=True)
