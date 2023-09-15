from fastapi import APIRouter

from . import (
    controller_public_cookbooks,
    controller_public_foods,
    controller_public_organizers,
    controller_public_recipes,
)

prefix = "/explore"

router = APIRouter()

router.include_router(controller_public_cookbooks.router, prefix=prefix, tags=["Explore: Cookbooks"])
router.include_router(controller_public_foods.router, prefix=prefix, tags=["Explore: Foods"])
router.include_router(controller_public_organizers.categories_router, prefix=prefix, tags=["Explore: Categories"])
router.include_router(controller_public_organizers.tags_router, prefix=prefix, tags=["Explore: Tags"])
router.include_router(controller_public_organizers.tools_router, prefix=prefix, tags=["Explore: Tools"])
router.include_router(controller_public_recipes.router, prefix=prefix, tags=["Explore: Recipes"])
