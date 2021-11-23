from fastapi import APIRouter

from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.recipe.recipe_tool_service import RecipeToolService

router = APIRouter()

router.include_router(RouterFactory(RecipeToolService, prefix="/tools", tags=["Recipes: Tools"]))
