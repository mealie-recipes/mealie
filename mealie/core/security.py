from datetime import datetime, timedelta
from pathlib import Path

from jose import jwt
from passlib.context import CryptContext

from mealie.core.config import get_settings
from mealie.db.database import get_database
from mealie.schema.user import PrivateUser

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(data: dict(), expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def create_file_token(file_path: Path) -> bool:
    token_data = {"file": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def authenticate_user(session, email: str, password: str) -> PrivateUser:
    db = get_database(session)

    user: PrivateUser = db.users.get(email, "email", any_case=True)

    if not user:
        user = db.users.get(email, "username", any_case=True)
    if not user:
        return False

    if not verify_password(password, user.password):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain string to a hashed password

    Args:
        plain_password (str): raw password string
        hashed_password (str): hashed password from the database

    Returns:
        bool: Returns True if a match return False
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving
    a new password to the database.

    Args:
        password (str): Password String

    Returns:
        str: Hashed Password
    """
    return pwd_context.hash(password)
