from fastapi import APIRouter

from . import (
    controller_cookbooks,
    controller_group_notifications,
    controller_group_recipe_actions,
    controller_household_self_service,
    controller_invitations,
    controller_mealplan,
    controller_mealplan_rules,
    controller_shopping_lists,
    controller_webhooks,
)

router = APIRouter()

router.include_router(controller_cookbooks.router)
router.include_router(controller_group_notifications.router)
router.include_router(controller_group_recipe_actions.router)
router.include_router(controller_household_self_service.router)
router.include_router(controller_invitations.router)
router.include_router(controller_shopping_lists.router)
router.include_router(controller_shopping_lists.item_router)
router.include_router(controller_webhooks.router)

# mealplan_rules must be added before mealplan due to the way the routes are defined
router.include_router(controller_mealplan_rules.router)
router.include_router(controller_mealplan.router)
