import contextlib
import json
from collections.abc import Callable
from enum import Enum
from json.decoder import JSONDecodeError
from pathlib import PurePath

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException

from mealie.core.dependencies import get_admin_user, get_current_user
from mealie.core.root_logger import get_logger
from mealie.schema.response import ErrorResponse

logger = get_logger()

# FastAPI's request handler uses this exact detail when multipart parsing raises.
_BODY_PARSE_ERROR_DETAIL = "There was an error parsing the body"
_TEMP_STORAGE_ERROR_MESSAGE = (
    "The server could not store the uploaded file. Check that temporary storage is available and try again."
)


def _traceback_includes_tempfile(exc: BaseException) -> bool:
    traceback = exc.__traceback__
    while traceback is not None:
        if PurePath(traceback.tb_frame.f_code.co_filename).name == "tempfile.py":
            return True
        traceback = traceback.tb_next
    return False


def _tempfile_oserror(exc: StarletteHTTPException) -> OSError | None:
    """OSError raised while spooling a multipart upload into temporary storage.

    Ordinary client multipart errors are re-raised by FastAPI and do not use the generic
    body-parsing detail, so they stay 400 responses.
    """
    if exc.status_code != status.HTTP_400_BAD_REQUEST or exc.detail != _BODY_PARSE_ERROR_DETAIL:
        return None

    seen: set[int] = set()
    current: BaseException | None = exc.__cause__
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, OSError) and _traceback_includes_tempfile(current):
            return current
        current = current.__cause__
    return None


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
            try:
                with contextlib.suppress(JSONDecodeError):
                    response = await original_route_handler(request)

                    # StreamingResponse from starlette doesn't have a body attribute, even though it
                    # inherits from Response, so we may get an attribute error here even though our
                    # type hinting suggests otherwise.
                    try:
                        response_body = json.loads(response.body)
                    except AttributeError:
                        return response

                    if isinstance(response_body, dict):
                        if last_modified := response_body.get("updatedAt"):
                            response.headers["last-modified"] = last_modified

                            # Force no-cache for all responses to prevent browser from caching API calls
                            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                return response
            except StarletteHTTPException as exc:
                temp_error = _tempfile_oserror(exc)
                if temp_error is None:
                    raise

                # A failed temp-file spool is a server fault. Log the OSError and return a
                # structured 500; the raw path and errno stay out of the response.
                logger.exception("Upload failed because temporary storage is unavailable")
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ErrorResponse.respond(_TEMP_STORAGE_ERROR_MESSAGE),
                ) from temp_error

        return custom_route_handler
