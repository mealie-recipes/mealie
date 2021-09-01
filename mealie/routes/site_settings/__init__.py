from fastapi import APIRouter

from . import site_settings

settings_router = APIRouter()

settings_router.include_router(site_settings.public_router)
settings_router.include_router(site_settings.admin_router)
