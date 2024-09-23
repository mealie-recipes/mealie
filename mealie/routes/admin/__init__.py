from mealie.routes._base.routers import AdminAPIRouter

from . import (
    admin_about,
    admin_backups,
    admin_debug,
    admin_email,
    admin_maintenance,
    admin_management_groups,
    admin_management_households,
    admin_management_users,
)

router = AdminAPIRouter(prefix="/admin")

router.include_router(admin_about.router, tags=["Admin: About"])
router.include_router(admin_management_users.router, tags=["Admin: Manage Users"])
router.include_router(admin_management_households.router, tags=["Admin: Manage Households"])
router.include_router(admin_management_groups.router, tags=["Admin: Manage Groups"])
router.include_router(admin_email.router, tags=["Admin: Email"])
router.include_router(admin_backups.router, tags=["Admin: Backups"])
router.include_router(admin_maintenance.router, tags=["Admin: Maintenance"])
router.include_router(admin_debug.router, tags=["Admin: Debug"])
