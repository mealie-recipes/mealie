from django.http import HttpRequest, HttpResponse
from django.urls import path

from mealie.drf_api.views import (
    AppInfoView,
    AppStartupInfoView,
    AppThemeView,
)


def redirect_about(request: HttpRequest) -> HttpResponse:
    target = request.path.removesuffix("/")
    if query := request.META.get("QUERY_STRING"):
        target = f"{target}?{query}"

    response = HttpResponse(status=307)
    response["Location"] = request.build_absolute_uri(target)
    return response


urlpatterns = [
    path("api/app/about", AppInfoView.as_view(), name="app-info"),
    path(
        "api/app/about/startup-info",
        AppStartupInfoView.as_view(),
        name="app-startup-info",
    ),
    path(
        "api/app/about/theme",
        AppThemeView.as_view(),
        name="app-theme",
    ),
    path("api/app/about/", redirect_about),
    path("api/app/about/startup-info/", redirect_about),
    path("api/app/about/theme/", redirect_about),
]
