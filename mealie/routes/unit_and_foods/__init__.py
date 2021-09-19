from mealie.services.recipe.recipe_unit_service import RecipeUnitService
from fastapi import APIRouter

from mealie.services._base_http_service.router_factory import RouterFactory
from mealie.services.recipe.recipe_food_service import RecipeFoodService


router = APIRouter()

router.include_router(RouterFactory(RecipeFoodService, prefix="/foods"), tags=["Recipes: Foods"])
router.include_router(RouterFactory(RecipeUnitService, prefix="/units"), tags=["Recipes: Units"])
