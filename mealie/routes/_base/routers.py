import contextlib
import json
from collections.abc import Callable
from enum import Enum
from json.decoder import JSONDecodeError

from fastapi import APIRouter, Depends, Request, Response
from fastapi.routing import APIRoute

from mealie.core.dependencies import get_admin_user, get_current_user


class AdminAPIRouter(APIRouter):
    """Router for functions to be protected behind admin authentication"""

    def __init__(self, tags: list[str | Enum] | None = None, prefix: str = "", **kwargs):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_admin_user)], **kwargs)


class UserAPIRouter(APIRouter):
    """Router for functions to be protected behind user authentication"""

    def __init__(self, tags: list[str | Enum] | None = None, prefix: str = "", **kwargs):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(get_current_user)], **kwargs)


class MealieCrudRoute(APIRoute):
    """Route class to include the last-modified header when returning a MealieModel, when available"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            with contextlib.suppress(JSONDecodeError):
                response = await original_route_handler(request)
                response_body = json.loads(response.body)
                if isinstance(response_body, dict):
                    if last_modified := response_body.get("updatedAt"):
                        response.headers["last-modified"] = last_modified

                        # Force no-cache for all responses to prevent browser from caching API calls
                        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return response

        return custom_route_handler
