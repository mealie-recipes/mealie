from fastapi import APIRouter, Request

from mealie.core.config import APP_VERSION, get_app_settings
from mealie.schema.admin.about import AppInfo

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
def get_app_info(request: Request):
    """Get general application information"""
    settings = get_app_settings()

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
        sso_login_available=settings.SSO_ENABLED and bool(request.headers.get(settings.SSO_TRUSTED_HEADER_USER, False))
    )
