from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from mealie.lang.providers import get_locale_config, get_locale_provider, set_locale_context


class LocaleContextMiddleware(BaseHTTPMiddleware):
    """
    Inject translator and locale config into context var.
    This allows any part of the app to call get_locale_context, as long as it's within an HTTP request context.
    """

    async def dispatch(self, request: Request, call_next):
        accept_language = request.headers.get("accept-language")
        translator = get_locale_provider(accept_language)
        locale_config = get_locale_config(accept_language)

        # Set context for this request
        set_locale_context(translator, locale_config)

        response = await call_next(request)
        return response
