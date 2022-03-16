from fastapi import APIRouter

from mealie.core.config import APP_VERSION, get_app_settings
from mealie.schema.admin.about import AppInfo

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
async def get_app_info():
    """Get general application information"""
    settings = get_app_settings()

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
    )
