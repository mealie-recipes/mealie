from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class TestUser:
    email: str
    user_id: UUID
    username: str
    password: str
    _group_id: UUID
    token: Any

    @property
    def group_id(self) -> str:
        return str(self._group_id)
