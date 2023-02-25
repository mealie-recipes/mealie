from logging import Logger

import fastapi
import sqlalchemy
from fastapi.responses import JSONResponse

from mealie.core import exceptions
from mealie.lang.providers import local_provider
from mealie.schema.response.responses import ErrorResponse


def json_error(content, status_code):
    return JSONResponse(content={"detail": content}, status_code=status_code)


def mount_handlers(app: fastapi.FastAPI, logger: Logger) -> None:
    """
    mount_handlers is a function that mounts the exception handlers to the FastAPI app.
    It provides a common handling point for known exceptions and provides a consistent
    response format.
    """

    @app.exception_handler(exceptions.PermissionDenied)
    def _(req: fastapi.Request, exc: exceptions.PermissionDenied):
        t = local_provider(req.headers.get("Accept-Language"))

        return json_error(
            ErrorResponse.respond(
                message=t.t("exceptions.permission-denied"),
                exception=exc.__class__.__name__,
            ),
            403,
        )

    @app.exception_handler(exceptions.NoEntryFound)
    def _(req: fastapi.Request, exc: exceptions.NoEntryFound):
        t = local_provider(req.headers.get("Accept-Language"))

        return json_error(
            ErrorResponse.respond(
                t.t("exceptions.no-entry-found"),
                exception=exc.__class__.__name__,
            ),
            404,
        )

    @app.exception_handler(sqlalchemy.exc.IntegrityError)
    def _(req: fastapi.Request, exc: sqlalchemy.exc.IntegrityError):
        t = local_provider(req.headers.get("Accept-Language"))

        return json_error(
            ErrorResponse.respond(
                message=t.t("exceptions.integrity-error"),
                exception=exc.__class__.__name__,
            ),
            400,
        )

    @app.exception_handler(Exception)
    def _(req: fastapi.Request, exc: Exception):
        logger.error("Unknown error")
        logger.exception(exc)

        return json_error(
            ErrorResponse.respond(
                message="Unknown Error",
                exception=exc.__class__.__name__,
            ),
            500,
        )
