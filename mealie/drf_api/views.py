from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mealie.core.config import get_app_settings
from mealie.schema.admin.about import AppTheme


class AppThemeView(APIView):
    http_method_names = ["get"]

    def get(self, request: Request) -> Response:
        settings = get_app_settings()
        theme = AppTheme(**settings.theme.model_dump())

        response = Response(theme.model_dump(mode="json", by_alias=True))
        response["Cache-Control"] = "public, max-age=604800"
        return response

    def http_method_not_allowed(self, request: Request, *args, **kwargs) -> Response:
        return Response(
            {"detail": "Method Not Allowed"},
            status=405,
        )
