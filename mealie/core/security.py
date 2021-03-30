from datetime import datetime, timedelta
from mealie.schema.user import UserInDB

from jose import jwt
from mealie.core.config import settings
from mealie.db.database import db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(data: dict(), expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def authenticate_user(session, email: str, password: str) -> UserInDB:
    user: UserInDB = db.users.get(session, email, "email")
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


def get_password_hash(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving
    a new password to the database.

    Args:
        password (str): Password String

    Returns:
        str: Hashed Password
    """
    return pwd_context.hash(password)
