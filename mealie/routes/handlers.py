from typing import Any

from mealie.core.root_logger import get_logger
from mealie.http.requests import Request

logger = get_logger()


def log_wrapper(request: Request, error: Any) -> None:
    logger.error("Start 422 Error".center(60, "-"))
    logger.error(f"{request.method} {request.url}")
    logger.error(f"error is {error}")
    logger.error("End 422 Error".center(60, "-"))
