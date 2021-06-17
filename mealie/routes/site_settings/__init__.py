from fastapi import APIRouter

from . import all_settings, custom_pages, site_settings

settings_router = APIRouter()

settings_router.include_router(all_settings.router)
settings_router.include_router(custom_pages.router)
settings_router.include_router(site_settings.router)
