from fastapi import APIRouter

from . import (
    controller_public_cookbooks,
    controller_public_foods,
    controller_public_households,
    controller_public_organizers,
    controller_public_recipes,
)

router = APIRouter(prefix="/explore/groups/{group_slug}")

# group
router.include_router(controller_public_foods.router, tags=["Explore: Foods"])
router.include_router(controller_public_households.router, tags=["Explore: Households"])
router.include_router(controller_public_organizers.categories_router, tags=["Explore: Categories"])
router.include_router(controller_public_organizers.tags_router, tags=["Explore: Tags"])
router.include_router(controller_public_organizers.tools_router, tags=["Explore: Tools"])

# household
router.include_router(controller_public_cookbooks.router, tags=["Explore: Cookbooks"])
router.include_router(controller_public_recipes.router, tags=["Explore: Recipes"])
