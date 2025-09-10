from dataclasses import dataclass
from typing import Any
from uuid import UUID

from mealie.db.models.users.users import AuthMethod
from mealie.repos.repository_factory import AllRepositories


@dataclass
class TestUser:
    email: str
    user_id: UUID
    username: str
    full_name: str
    password: str
    _group_id: UUID
    _household_id: UUID
    token: Any
    auth_method = AuthMethod.MEALIE
    repos: AllRepositories

    @property
    def group_id(self) -> str:
        return str(self._group_id)

    @property
    def household_id(self) -> str:
        return str(self._household_id)
