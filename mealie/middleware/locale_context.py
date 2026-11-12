from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from mealie.lang.providers import get_locale_config, get_locale_provider, set_locale_context


class LocaleContextMiddleware:
    """
    Inject translator and locale config into context var.
    This allows any part of the app to call get_locale_context, as long as it's within an HTTP request context.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        accept_language = Headers(scope=scope).get("accept-language")
        translator = get_locale_provider(accept_language)
        locale_config = get_locale_config(accept_language)

        # Set context for this request
        set_locale_context(translator, locale_config)

        await self.app(scope, receive, send)
