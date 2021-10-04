from fastapi import APIRouter

from mealie.routes.routers import AdminAPIRouter

from . import admin_about, admin_email, admin_group, admin_log

router = AdminAPIRouter(prefix="/admin")

router.include_router(admin_about.router, tags=["Admin: About"])
router.include_router(admin_log.router, tags=["Admin: Log"])
router.include_router(admin_group.router, tags=["Admin: Group"])
router.include_router(admin_email.router, tags=["Admin: Email"])
