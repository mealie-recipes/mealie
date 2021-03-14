from fastapi import APIRouter
from routes.mealplans import crud, helpers

router = APIRouter()

router.include_router(crud.router)
router.include_router(helpers.router)
