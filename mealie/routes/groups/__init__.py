from fastapi import APIRouter

from . import (
    controller_group_households,
    controller_group_reports,
    controller_group_self_service,
    controller_labels,
    controller_migrations,
    controller_seeder,
)

router = APIRouter()

router.include_router(controller_group_households.router)
router.include_router(controller_group_self_service.router)
router.include_router(controller_migrations.router)
router.include_router(controller_group_reports.router)
router.include_router(controller_labels.router)
router.include_router(controller_seeder.router)
