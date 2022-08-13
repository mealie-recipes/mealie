from datetime import datetime

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user.user import PrivateUser
from mealie.services._base_service import BaseService


class UserService(BaseService):
    def __init__(self, repos: AllRepositories) -> None:
        self.repos = repos
        super().__init__()

    def get_locked_users(self) -> list[PrivateUser]:
        return self.repos.users.get_locked_users()

    def lock_user(self, user: PrivateUser) -> PrivateUser:
        user.locked_at = datetime.now()
        return self.repos.users.update(user.id, user)

    def unlock_user(self, user: PrivateUser) -> PrivateUser:
        user.locked_at = None
        user.login_attemps = 0
        return self.repos.users.update(user.id, user)
