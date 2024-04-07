from enum import Enum

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class RecipeActionType(Enum):
    link = "link"


class CreateGroupRecipeAction(MealieModel):
    action_type: RecipeActionType
    title: str
    url: str

    model_config = ConfigDict(use_enum_values=True)


class SaveGroupRecipeAction(CreateGroupRecipeAction):
    group_id: UUID4


class GroupRecipeActionOut(SaveGroupRecipeAction):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)


class GroupRecipeActionPagination(PaginationBase):
    items: list[GroupRecipeActionOut]
