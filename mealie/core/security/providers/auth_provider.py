import abc
from datetime import datetime, timedelta, timezone

from fastapi import Request
from jose import jwt
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user import PrivateUser

ALGORITHM = "HS256"
remember_me_duration = timedelta(days=14)


class AuthProvider(metaclass=abc.ABCMeta):
    """Base Authentication Provider interface"""

    def __init__(self, session: Session, request: Request) -> None:
        self.session = session
        self.request = request
        self.user: PrivateUser | None = None
        self.__has_tried_user = False

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return hasattr(__subclass, "authenticate") and callable(__subclass.authenticate)

    def get_access_token(self, user: PrivateUser, remember_me=False) -> tuple[str, timedelta]:
        settings = get_app_settings()

        duration = timedelta(hours=settings.TOKEN_TIME)
        if remember_me and remember_me_duration > duration:
            duration = remember_me_duration

        return AuthProvider.create_access_token({"sub": str(user.id)}, duration)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, timedelta]:
        settings = get_app_settings()

        to_encode = data.copy()
        expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

        expire = datetime.now(timezone.utc) + expires_delta

        to_encode["exp"] = expire
        return (jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM), expires_delta)

    def try_get_user(self, username: str) -> PrivateUser | None:
        """Try to get a user from the database, first trying username, then trying email"""
        if self.__has_tried_user:
            return self.user

        db = get_repositories(self.session)

        user = user = db.users.get_one(username, "username", any_case=True)
        if not user:
            user = db.users.get_one(username, "email", any_case=True)

        self.user = user
        return user

    @abc.abstractmethod
    async def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user"""
        raise NotImplementedError
