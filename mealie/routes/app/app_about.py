from fastapi import APIRouter, Response

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.schema.admin.about import AppInfo, AppTheme

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
def get_app_info():
    """Get general application information"""
    settings = get_app_settings()

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
    )


@router.get("/theme", response_model=AppTheme)
def get_app_theme(resp: Response):
    """Get's the current theme settings"""
    settings = get_app_settings()

    resp.headers["Cache-Control"] = "public, max-age=604800"
    return AppTheme(**settings.theme.dict())
