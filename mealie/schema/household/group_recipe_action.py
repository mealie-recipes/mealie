from enum import Enum
from typing import Any

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase

# ==================================================================================================================
# CRUD


class GroupRecipeActionType(Enum):
    link = "link"
    post = "post"


class CreateGroupRecipeAction(MealieModel):
    action_type: GroupRecipeActionType
    title: str
    url: str

    model_config = ConfigDict(use_enum_values=True)


class SaveGroupRecipeAction(CreateGroupRecipeAction):
    group_id: UUID4
    household_id: UUID4


class GroupRecipeActionOut(SaveGroupRecipeAction):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)


class GroupRecipeActionPagination(PaginationBase):
    items: list[GroupRecipeActionOut]


# ==================================================================================================================
# Actions


class GroupRecipeActionPayload(MealieModel):
    action: GroupRecipeActionOut
    content: Any
