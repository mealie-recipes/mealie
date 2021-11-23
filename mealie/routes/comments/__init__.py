from fastapi import APIRouter

from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.recipe.recipe_comments_service import RecipeCommentsService

router = APIRouter()

router.include_router(RouterFactory(RecipeCommentsService, prefix="/comments", tags=["Recipe: Comments"]))
