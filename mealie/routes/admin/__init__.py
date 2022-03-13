from mealie.routes._base.routers import AdminAPIRouter

from . import (
    admin_about,
    admin_backups,
    admin_email,
    admin_log,
    admin_management_groups,
    admin_management_users,
    admin_server_tasks,
)

router = AdminAPIRouter(prefix="/admin")

router.include_router(admin_about.router, tags=["Admin: About"])
router.include_router(admin_log.router, tags=["Admin: Log"])
router.include_router(admin_management_users.router)
router.include_router(admin_management_groups.router)
router.include_router(admin_email.router, tags=["Admin: Email"])
router.include_router(admin_server_tasks.router, tags=["Admin: Server Tasks"])
router.include_router(admin_backups.router)
