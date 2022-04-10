import rich
from fastapi import APIRouter, Depends

from mealie.core.config import APP_VERSION, get_app_settings
from mealie.lang.providers import Translator, local_provider
from mealie.schema.admin.about import AppInfo

router = APIRouter(prefix="/about")


@router.get("", response_model=AppInfo)
def get_app_info(local: Translator = Depends(local_provider)):
    """Get general application information"""
    settings = get_app_settings()
    rich.inspect(local)

    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
        allow_signup=settings.ALLOW_SIGNUP,
    )
