from datetime import timedelta

from fastapi import Request
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.core.exceptions import UserLockedOut
from mealie.core.security.hasher import get_hasher
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.repos.all_repositories import get_repositories
from mealie.services.user_services.user_service import UserService


class CredentialsRequest:
    """Class that represents a user's credentials from the login form"""

    def __init__(self, username: str, password: str, remember_me: bool = False):
        self.username = username
        self.password = password
        self.remember_me = remember_me


class CredentialsProvider(AuthProvider):
    """Authentication provider that authenticates a user the database using username/password combination"""

    def __init__(self, session: Session, request: Request) -> None:
        super().__init__(session, request)
        self.request_data: CredentialsRequest | None = None

    async def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""
        data = await self.get_request_data()
        settings = get_app_settings()
        db = get_repositories(self.session)
        user = self.try_get_user(data.username)

        if not user:
            # To prevent user enumeration we perform the verify_password computation to ensure
            # server side time is relatively constant and not vulnerable to timing attacks.
            CredentialsProvider.verify_password(
                "abc123cba321", "$2b$12$JdHtJOlkPFwyxdjdygEzPOtYmdQF5/R5tHxw5Tq8pxjubyLqdIX5i"
            )
            return None

        if user.login_attemps >= settings.SECURITY_MAX_LOGIN_ATTEMPTS or user.is_locked:
            raise UserLockedOut()

        if not CredentialsProvider.verify_password(data.password, user.password):
            user.login_attemps += 1
            db.users.update(user.id, user)

            if user.login_attemps >= settings.SECURITY_MAX_LOGIN_ATTEMPTS:
                user_service = UserService(db)
                user_service.lock_user(user)

            return None

        user.login_attemps = 0
        user = db.users.update(user.id, user)
        return self.get_access_token(user, data.remember_me)  # type: ignore

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compares a plain string to a hashed password"""
        return get_hasher().verify(plain_password, hashed_password)

    async def get_request_data(self) -> CredentialsRequest:
        """Get the credentials request"""
        if self.request_data:
            return self.request_data

        data = await self.request.form()
        self.request_data = CredentialsRequest(data.get("username"), data.get("password"), data.get("remember_me"))
        return self.request_data
