from typing import Any

from mealie.lang.providers import get_locale_config, get_locale_provider, set_locale_context


class LocaleContextMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        accept_language = request.headers.get("accept-language")
        set_locale_context(get_locale_provider(accept_language), get_locale_config(accept_language))
        return self.get_response(request)
