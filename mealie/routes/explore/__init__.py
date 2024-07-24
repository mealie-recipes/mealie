from fastapi import APIRouter

from . import (
    controller_public_cookbooks,
    controller_public_foods,
    controller_public_organizers,
    controller_public_recipes,
)

group_prefix = "/explore/groups/{group_slug}"
household_prefix = "/explore/groups/{group_slug}/households/{household_slug}"

router = APIRouter()

# group
router.include_router(controller_public_foods.router, prefix=group_prefix, tags=["Explore: Foods"])
router.include_router(controller_public_organizers.categories_router, prefix=group_prefix, tags=["Explore: Categories"])
router.include_router(controller_public_organizers.tags_router, prefix=group_prefix, tags=["Explore: Tags"])
router.include_router(controller_public_organizers.tools_router, prefix=group_prefix, tags=["Explore: Tools"])

# household
router.include_router(controller_public_cookbooks.router, prefix=household_prefix, tags=["Explore: Cookbooks"])
router.include_router(controller_public_recipes.router, prefix=household_prefix, tags=["Explore: Recipes"])
