from typing import Optional

from fastapi import APIRouter, Depends

from mealie.core.dependencies import get_admin_user, get_current_user


class AdminAPIRouter(APIRouter):
    """Router for functions to be protected behind admin authentication"""

    def __init__(
        self,
        tags: Optional[list[str]] = None,
        prefix: str = "",
    ):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_admin_user)])


class UserAPIRouter(APIRouter):
    """Router for functions to be protected behind user authentication"""

    def __init__(
        self,
        tags: Optional[list[str]] = None,
        prefix: str = "",
    ):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_current_user)])
