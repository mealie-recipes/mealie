from fastapi import APIRouter

from . import crud, helpers, mealplans

meal_plan_router = APIRouter()

meal_plan_router.include_router(crud.router)
meal_plan_router.include_router(crud.public_router)
meal_plan_router.include_router(helpers.router)
meal_plan_router.include_router(mealplans.router)
