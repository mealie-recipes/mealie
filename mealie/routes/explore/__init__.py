from fastapi import APIRouter

from . import controller_public_recipes

router = APIRouter()

router.include_router(controller_public_recipes.router)
