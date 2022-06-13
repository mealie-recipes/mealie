import json
from collections.abc import Callable
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Optional, Union

from fastapi import APIRouter, Depends, Request, Response
from fastapi.routing import APIRoute

from mealie.core.dependencies import get_admin_user, get_current_user


class AdminAPIRouter(APIRouter):
    """Router for functions to be protected behind admin authentication"""

    def __init__(self, tags: Optional[list[Union[str, Enum]]] = None, prefix: str = "", **kwargs):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_admin_user)], **kwargs)


class UserAPIRouter(APIRouter):
    """Router for functions to be protected behind user authentication"""

    def __init__(self, tags: Optional[list[Union[str, Enum]]] = None, prefix: str = "", **kwargs):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_current_user)], **kwargs)


class MealieCrudRoute(APIRoute):
    """Route class to include the last-modified header when returning a MealieModel, when available"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                response = await original_route_handler(request)
                response_body = json.loads(response.body)
                if type(response_body) == dict:
                    if last_modified := response_body.get("updateAt"):
                        response.headers["last-modified"] = last_modified

            except JSONDecodeError:
                pass

            return response

        return custom_route_handler
