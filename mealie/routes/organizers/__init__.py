from fastapi import APIRouter

from . import controller_categories, controller_tags, controller_tools

router = APIRouter(prefix="/organizers")
router.include_router(controller_categories.router)
router.include_router(controller_tags.router)
router.include_router(controller_tools.router)
