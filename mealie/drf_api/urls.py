from django.http import HttpRequest, HttpResponse
from django.urls import path

from mealie.drf_api.views import AppThemeView


def redirect_theme(request: HttpRequest) -> HttpResponse:
    target = "/api/app/about/theme"
    if query := request.META.get("QUERY_STRING"):
        target = f"{target}?{query}"

    response = HttpResponse(status=307)
    response["Location"] = request.build_absolute_uri(target)
    return response


urlpatterns = [
    path(
        "api/app/about/theme",
        AppThemeView.as_view(),
        name="app-theme",
    ),
    path(
        "api/app/about/theme/",
        redirect_theme,
        name="app-theme-redirect",
    ),
]
