from fastapi import APIRouter

from . import admin_about, admin_log

router = APIRouter(prefix="/admin")

router.include_router(admin_about.router, tags=["Admin: About"])
router.include_router(admin_log.router, tags=["Admin: Log"])
