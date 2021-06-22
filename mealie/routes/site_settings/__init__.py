from fastapi import APIRouter

from . import custom_pages, site_settings

settings_router = APIRouter()

settings_router.include_router(custom_pages.public_router)
settings_router.include_router(custom_pages.admin_router)
settings_router.include_router(site_settings.public_router)
settings_router.include_router(site_settings.admin_router)
