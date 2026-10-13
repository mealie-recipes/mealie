from typing import Any

from rest_framework.negotiation import DefaultContentNegotiation


class MealieContentNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request: Any, renderers: Any, format_suffix: Any = None) -> Any:
        return renderers[0], renderers[0].media_type

    def select_parser(self, request: Any, parsers: Any) -> Any:
        media = request.content_type.split(";", 1)[0].strip().lower()
        if not media or media == "application/json" or media.startswith("application/") and media.endswith("+json"):
            from mealie.http.parsers import JSONParser

            return next(parser for parser in parsers if isinstance(parser, JSONParser))
        return super().select_parser(request, parsers)
