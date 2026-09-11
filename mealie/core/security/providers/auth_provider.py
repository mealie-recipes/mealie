import abc
from datetime import timedelta

from sqlalchemy.orm.session import Session

from mealie.core.security.tokens import create_access_token
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user import PrivateUser


class AuthProvider[T](metaclass=abc.ABCMeta):
    """Base Authentication Provider interface"""

    def __init__(self, session: Session, data: T) -> None:
        self.session = session
        self.data = data
        self.user: PrivateUser | None = None
        self.__has_tried_user = False

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return hasattr(__subclass, "authenticate") and callable(__subclass.authenticate)

    def get_access_token(self, user: PrivateUser, remember_me: bool = False) -> tuple[str, timedelta]:
        """Mints a session token for a user who has just been authenticated.

        Every session lasts `TOKEN_TIME`. Remember-me decides whether the client keeps the token past
        the end of the browser session, not how long it is valid for, so it travels on the token as
        the `rme` claim for the client to act on — and survives refreshes intact.
        """
        return create_access_token({"sub": str(user.id), "rme": remember_me})

    def try_get_user(self, username: str) -> PrivateUser | None:
        """Try to get a user from the database, first trying username, then trying email"""
        if self.__has_tried_user:
            return self.user

        db = get_repositories(self.session, group_id=None, household_id=None)

        user = user = db.users.get_one(username, "username", any_case=True)
        if not user:
            user = db.users.get_one(username, "email", any_case=True)

        self.user = user
        return user

    @abc.abstractmethod
    def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user"""
        raise NotImplementedError
