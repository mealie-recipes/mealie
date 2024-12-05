from datetime import UTC, datetime

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user.user import PrivateUser
from mealie.services._base_service import BaseService


class UserService(BaseService):
    def __init__(self, repos: AllRepositories) -> None:
        self.repos = repos
        super().__init__()

    def get_locked_users(self) -> list[PrivateUser]:
        return self.repos.users.get_locked_users()

    def reset_locked_users(self, force: bool = False) -> int:
        """
        Queriers that database for all locked users and resets their locked_at field to None
        if more than the set time has passed since the user was locked
        """
        locked_users = self.get_locked_users()

        unlocked = 0

        for user in locked_users:
            if force or not user.is_locked and user.locked_at is not None:
                self.unlock_user(user)
                unlocked += 1

        return unlocked

    def lock_user(self, user: PrivateUser) -> PrivateUser:
        user.locked_at = datetime.now(UTC)
        return self.repos.users.update(user.id, user)

    def unlock_user(self, user: PrivateUser) -> PrivateUser:
        user.locked_at = None
        user.login_attemps = 0
        return self.repos.users.update(user.id, user)
