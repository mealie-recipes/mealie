from fastapi import APIRouter
from mealie.routes.site_settings import custom_pages, site_settings

router = APIRouter()

router.include_router(custom_pages.router)
router.include_router(site_settings.router)
