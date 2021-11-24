from fastapi import APIRouter

from mealie.routes.routers import AdminAPIRouter
from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.admin.admin_user_service import AdminUserService

from . import admin_about, admin_email, admin_group, admin_log, admin_server_tasks

router = AdminAPIRouter(prefix="/admin")

router.include_router(admin_about.router, tags=["Admin: About"])
router.include_router(admin_log.router, tags=["Admin: Log"])
router.include_router(admin_group.router, tags=["Admin: Group"])
router.include_router(RouterFactory(AdminUserService, prefix="/users", tags=["Admin: Users"]))
router.include_router(admin_email.router, tags=["Admin: Email"])
router.include_router(admin_server_tasks.router, tags=["Admin: Server Tasks"])
