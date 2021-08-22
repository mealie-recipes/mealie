from fastapi import APIRouter

from . import food_routes, unit_routes

router = APIRouter()

router.include_router(food_routes.router, prefix="/foods", tags=["Recipes: Foods"])
router.include_router(unit_routes.router, prefix="/units", tags=["Recipes: Units"])
