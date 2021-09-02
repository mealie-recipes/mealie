from fastapi import APIRouter

from mealie.services.base_http_service import RouterFactory
from mealie.services.cookbook.cookbook_service import CookbookService
from mealie.services.group.webhook_service import WebhookService

from . import categories, crud, self_service

router = APIRouter()

webhook_router = RouterFactory(service=WebhookService, prefix="/groups/webhooks", tags=["Groups: Webhooks"])
cookbook_router = RouterFactory(service=CookbookService, prefix="/groups/cookbooks", tags=["Groups: Cookbooks"])
router.include_router(self_service.user_router)
router.include_router(cookbook_router)
router.include_router(categories.user_router)
router.include_router(webhook_router)
router.include_router(crud.user_router)
router.include_router(crud.admin_router)
