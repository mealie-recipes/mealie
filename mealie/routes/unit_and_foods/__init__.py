from fastapi import APIRouter

from . import food_routes, unit_routes

units_and_foods_router = APIRouter(tags=["Food and Units"])

units_and_foods_router.include_router(food_routes.router)
units_and_foods_router.include_router(unit_routes.router)
