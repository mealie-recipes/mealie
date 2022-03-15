from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger

logger = get_logger()


def log_wrapper(request: Request, e):
    logger.error("Start 422 Error".center(60, "-"))
    logger.error(f"{request.method} {request.url}")
    logger.error(f"error is {e}")
    logger.error("End 422 Error".center(60, "-"))


def register_debug_handler(app: FastAPI):
    settings = get_app_settings()

    if settings.PRODUCTION and not settings.TESTING:
        return

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        log_wrapper(request, exc)
        content = {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "message": exc_str, "data": None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return validation_exception_handler
