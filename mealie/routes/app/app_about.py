from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.db.db_setup import generate_session
from mealie.db.models.users.users import User
from mealie.repos.all_repositories import get_repositories
from mealie.schema.admin.about import AppInfo, AppStartupInfo, AppTheme

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
def get_app_info(session: Session = Depends(generate_session)):
    """Get general application information"""
    settings = get_app_settings()

    public_repos = get_repositories(session, group_id=None, household_id=None)

    default_group_slug: str | None = None
    default_household_slug: str | None = None

    default_group = public_repos.groups.get_by_name(settings.DEFAULT_GROUP)
    if default_group and default_group.preferences and not default_group.preferences.private_group:
        default_group_slug = default_group.slug

    if default_group and default_group_slug:
        group_repos = get_repositories(session, group_id=default_group.id, household_id=None)
        default_household = group_repos.households.get_by_name(settings.DEFAULT_HOUSEHOLD)
        if default_household and default_household.preferences and not default_household.preferences.private_household:
            default_household_slug = default_household.slug

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
        default_group_slug=default_group_slug,
        default_household_slug=default_household_slug,
        enable_oidc=settings.OIDC_READY,
        oidc_redirect=settings.OIDC_AUTO_REDIRECT,
        oidc_provider_name=settings.OIDC_PROVIDER_NAME,
        enable_openai=settings.OPENAI_ENABLED,
        enable_openai_image_services=settings.OPENAI_ENABLED and settings.OPENAI_ENABLE_IMAGE_SERVICES,
        allow_password_login=settings.ALLOW_PASSWORD_LOGIN,
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
