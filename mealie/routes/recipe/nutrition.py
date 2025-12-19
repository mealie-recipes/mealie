from fastapi import APIRouter

from mealie.routes._base import BaseUserController, controller
from mealie.schema.recipe.recipe_nutrition import FdcNutritionItem
from mealie.services.nutrition.nutrition_service import NutritionService

router = APIRouter(prefix="/nutrition")


@controller(router)
class NutritionController(BaseUserController):
    @router.get("/fetch_fda/{fdc_id}", response_model=list[FdcNutritionItem])
    async def fetch_external(self, fdc_id: str):
        nutrition_service = NutritionService()
        return nutrition_service.fdc(fdc_id)
