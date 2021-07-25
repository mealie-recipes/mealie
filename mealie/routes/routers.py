from fastapi import APIRouter, Depends
from mealie.routes.deps import get_admin_user, get_current_user

from typing import List, Optional


class AdminAPIRouter(APIRouter):
    """ Router for functions to be protected behind admin authentication """

    def __init__(
        self,
        tags: Optional[List[str]] = None,
        prefix: str = "",
    ):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_admin_user)])


class UserAPIRouter(APIRouter):
    """ Router for functions to be protected behind user authentication """

    def __init__(
        self,
        tags: Optional[List[str]] = None,
        prefix: str = "",
    ):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_current_user)])
