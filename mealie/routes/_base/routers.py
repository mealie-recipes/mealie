from enum import Enum
from typing import Any

from mealie.core.dependencies import get_admin_user, get_current_user
from mealie.http.api import APIRouter, Depends


class AdminAPIRouter(APIRouter):
    """Routes restricted to administrators by Mealie's existing user checks."""

    def __init__(self, tags: list[str | Enum] | None = None, prefix: str = "", **kwargs: Any) -> None:
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_admin_user)], **kwargs)


class UserAPIRouter(APIRouter):
    def __init__(self, tags: list[str | Enum] | None = None, prefix: str = "", **kwargs: Any) -> None:
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_current_user)], **kwargs)


class MealieCrudRoute:
    """Include modification and cache headers on CRUD responses."""

    last_modified = True
