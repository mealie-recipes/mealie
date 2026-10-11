from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.db.db_setup import session_context
from mealie.db.models.users.users import User
from mealie.repos.all_repositories import get_repositories
from mealie.schema.admin.about import AppInfo, AppStartupInfo, AppTheme


class PublicAboutView(APIView):
    """GET-only public view preserving FastAPI's method error response."""

    http_method_names = ["get"]

    def http_method_not_allowed(self, request: Request, *args, **kwargs) -> Response:
        return Response(
            {"detail": "Method Not Allowed"},
            status=405,
        )


class AppThemeView(PublicAboutView):
    def get(self, request: Request) -> Response:
        settings = get_app_settings()
        theme = AppTheme(**settings.theme.model_dump())

        response = Response(theme.model_dump(mode="json", by_alias=True))
        response["Cache-Control"] = "public, max-age=604800"
        return response


class AppInfoView(PublicAboutView):
    def get(self, request: Request) -> Response:
        settings = get_app_settings()

        with session_context() as session:
            public_repos = get_repositories(
                session,
                group_id=None,
                household_id=None,
            )

            default_group_slug: str | None = None
            default_household_slug: str | None = None

            default_group = public_repos.groups.get_by_name(settings.DEFAULT_GROUP)

            if default_group and default_group.preferences and not default_group.preferences.private_group:
                default_group_slug = default_group.slug

            if default_group and default_group_slug:
                group_repos = get_repositories(
                    session,
                    group_id=default_group.id,
                    household_id=None,
                )
                default_household = group_repos.households.get_by_name(settings.DEFAULT_HOUSEHOLD)

                if (
                    default_household
                    and default_household.preferences
                    and not default_household.preferences.private_household
                ):
                    default_household_slug = default_household.slug

            info = AppInfo(
                version=APP_VERSION,
                demo_status=settings.IS_DEMO,
                production=settings.PRODUCTION,
                allow_signup=settings.ALLOW_SIGNUP,
                default_group_slug=default_group_slug,
                default_household_slug=default_household_slug,
                enable_oidc=settings.OIDC_READY,
                oidc_redirect=settings.OIDC_AUTO_REDIRECT,
                oidc_provider_name=settings.OIDC_PROVIDER_NAME,
                allow_password_login=settings.ALLOW_PASSWORD_LOGIN,
                token_time=settings.TOKEN_TIME,
                allowed_iframe_hosts=settings.allowed_iframe_hosts,
            )

            payload = info.model_dump(mode="json", by_alias=True)

        return Response(payload)


class AppStartupInfoView(PublicAboutView):
    def get(self, request: Request) -> Response:
        settings = get_app_settings()

        with session_context() as session:
            is_first_login = session.query(User).filter_by(email=settings._DEFAULT_EMAIL).count() > 0

        info = AppStartupInfo(
            is_first_login=is_first_login,
            is_demo=settings.IS_DEMO,
        )

        return Response(info.model_dump(mode="json", by_alias=True))
