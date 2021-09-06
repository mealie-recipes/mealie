from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe.recipe_category import CategoryBase
from mealie.services.group_services.group_service import GroupSelfService

user_router = UserAPIRouter(prefix="/groups/categories", tags=["Groups: Mealplan Categories"])


@user_router.get("", response_model=list[CategoryBase])
def get_mealplan_categories(group_service: GroupSelfService = Depends(GroupSelfService.read_existing)):
    return group_service.item.categories


@user_router.put("", response_model=list[CategoryBase])
def update_mealplan_categories(
    new_categories: list[CategoryBase], group_service: GroupSelfService = Depends(GroupSelfService.write_existing)
):

    items = group_service.update_categories(new_categories)

    return items.categories
