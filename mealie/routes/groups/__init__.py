from fastapi import APIRouter

from . import (
    controller_cookbooks,
    controller_group_notifications,
    controller_group_reports,
    controller_group_self_service,
    controller_invitations,
    controller_labels,
    controller_mealplan,
    controller_mealplan_config,
    controller_mealplan_rules,
    controller_migrations,
    controller_shopping_lists,
    controller_webhooks,
)

router = APIRouter()

router.include_router(controller_group_self_service.router)
router.include_router(controller_mealplan_rules.router)
router.include_router(controller_mealplan_config.router)
router.include_router(controller_mealplan.router)
router.include_router(controller_cookbooks.router)
router.include_router(controller_webhooks.router)
router.include_router(controller_invitations.router)
router.include_router(controller_migrations.router)
router.include_router(controller_group_reports.router)
router.include_router(controller_shopping_lists.router)
router.include_router(controller_shopping_lists.item_router)
router.include_router(controller_labels.router)
router.include_router(controller_group_notifications.router)
