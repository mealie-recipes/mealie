from fastapi import APIRouter

from mealie.services._base_http_service import RouterFactory
from mealie.services.group_services import CookbookService, WebhookService
from mealie.services.group_services.meal_service import MealService

from . import categories, invitations, preferences, self_service

router = APIRouter()

webhook_router = RouterFactory(service=WebhookService, prefix="/groups/webhooks", tags=["Groups: Webhooks"])
cookbook_router = RouterFactory(service=CookbookService, prefix="/groups/cookbooks", tags=["Groups: Cookbooks"])
meal_plan_router = RouterFactory(service=MealService, prefix="/groups/mealplans", tags=["Groups: Mealplans"])
router.include_router(self_service.user_router)
router.include_router(cookbook_router)
router.include_router(meal_plan_router)
router.include_router(categories.user_router)
router.include_router(webhook_router)
router.include_router(invitations.router, prefix="/groups/invitations", tags=["Groups: Invitations"])
router.include_router(preferences.router, prefix="/groups/preferences", tags=["Group: Preferences"])
