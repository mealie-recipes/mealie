from fastapi import APIRouter, Depends

from mealie.schema.recipe.recipe_tool import RecipeToolResponse
from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.recipe.recipe_tool_service import RecipeToolService

router = APIRouter()

tools_router = RouterFactory(RecipeToolService, prefix="/tools", tags=["Recipes: Tools"])


@tools_router.get("/slug/{slug}")
async def Func(slug: str, tools_service: RecipeToolService = Depends(RecipeToolService.private)):
    """Returns a recipe by slug."""
    return tools_service.db.tools.get_one(slug, "slug", override_schema=RecipeToolResponse)


router.include_router(tools_router)
