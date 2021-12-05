from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.shared.recipe_shared_service import RecipeShareTokenSummary, SharedRecipeService

router = UserAPIRouter(prefix="/shared")

shared_router = RouterFactory(SharedRecipeService, prefix="/recipes", tags=["Shared: Recipes"])


@shared_router.get("", response_model=list[RecipeShareTokenSummary])
def get_all_shared(
    recipe_id: int = None,
    shared_recipe_service: SharedRecipeService = Depends(SharedRecipeService.private),
):
    """
    Get all shared recipes
    """
    return shared_recipe_service.get_all(recipe_id)


router.include_router(shared_router)
