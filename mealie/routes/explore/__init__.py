from fastapi import APIRouter, HTTPException

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicController
from mealie.schema.group.group_preferences import ReadGroupPreferences

from . import (
    controller_public_cookbooks,
    controller_public_foods,
    controller_public_households,
    controller_public_organizers,
    controller_public_recipes,
)

groups_router = APIRouter()


@controller(groups_router)
class PublicGroupsController(BasePublicController):
    @property
    def groups(self):
        return self.repos.groups

    @groups_router.get("/{group_slug}/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self, group_slug: str) -> ReadGroupPreferences:
        group = self.get_public_group(group_slug)
        if not group.preferences:
            raise HTTPException(404, "group preferences not found")
        return group.preferences


router = APIRouter(prefix="/explore/groups")
router.include_router(groups_router, tags=["Explore: Groups"])

prefix = "/{group_slug}"
router.include_router(controller_public_foods.router, tags=["Explore: Foods"], prefix=prefix)
router.include_router(controller_public_households.router, tags=["Explore: Households"], prefix=prefix)
router.include_router(controller_public_organizers.categories_router, tags=["Explore: Categories"], prefix=prefix)
router.include_router(controller_public_organizers.tags_router, tags=["Explore: Tags"], prefix=prefix)
router.include_router(controller_public_organizers.tools_router, tags=["Explore: Tools"], prefix=prefix)
router.include_router(controller_public_cookbooks.router, tags=["Explore: Cookbooks"], prefix=prefix)
router.include_router(controller_public_recipes.router, tags=["Explore: Recipes"], prefix=prefix)
