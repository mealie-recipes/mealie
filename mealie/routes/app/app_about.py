from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.db.db_setup import generate_session
from mealie.db.models.users.users import User
from mealie.repos.all_repositories import get_repositories
from mealie.schema.admin.about import AppInfo, AppStartupInfo, AppTheme, OIDCInfo

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
def get_app_info(session: Session = Depends(generate_session)):
    """Get general application information"""
    settings = get_app_settings()

    repos = get_repositories(session)
    default_group = repos.groups.get_by_name(settings.DEFAULT_GROUP)
    if default_group and default_group.preferences and not default_group.preferences.private_group:
        default_group_slug = default_group.slug
    else:
        default_group_slug = None

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
        default_group_slug=default_group_slug,
        enable_oidc=settings.OIDC_READY,
        oidc_redirect=settings.OIDC_AUTO_REDIRECT,
        oidc_provider_name=settings.OIDC_PROVIDER_NAME,
        enable_openai=settings.OPENAI_ENABLED,
    )


@router.get("/startup-info", response_model=AppStartupInfo)
def get_startup_info(session: Session = Depends(generate_session)):
    """returns helpful startup information"""
    settings = get_app_settings()

    is_first_login = False
    with session as db:
        if db.query(User).filter_by(email=settings._DEFAULT_EMAIL).count() > 0:
            is_first_login = True

    return AppStartupInfo(
        is_first_login=is_first_login,
        is_demo=settings.IS_DEMO,
    )


@router.get("/theme", response_model=AppTheme)
def get_app_theme(resp: Response):
    """Get's the current theme settings"""
    settings = get_app_settings()

    resp.headers["Cache-Control"] = "public, max-age=604800"
    return AppTheme(**settings.theme.model_dump())


@router.get("/oidc", response_model=OIDCInfo)
def get_oidc_info(resp: Response):
    """Get's the current OIDC configuration needed for the frontend"""
    settings = get_app_settings()

    resp.headers["Cache-Control"] = "public, max-age=604800"
    return OIDCInfo(
        configuration_url=settings.OIDC_CONFIGURATION_URL,
        client_id=settings.OIDC_CLIENT_ID,
        groups_claim=settings.OIDC_GROUPS_CLAIM if settings.OIDC_USER_GROUP or settings.OIDC_ADMIN_GROUP else None,
    )
