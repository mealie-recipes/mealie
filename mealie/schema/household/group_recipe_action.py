from enum import Enum
from typing import Any

from pydantic import UUID4, ConfigDict, field_validator

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

    @field_validator("url")
    def validate_url_scheme(url: str) -> str:
        """Validate that the URL uses a safe scheme to prevent XSS via javascript: URIs."""
        url_lower = url.lower().strip()
        if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
            raise ValueError("URL must use http or https scheme")
        return url


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
    recipe_scale: float
