from datetime import datetime
from typing import Annotated

from pydantic import UUID4, ConfigDict, StringConstraints
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeComment
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase


class UserBase(MealieModel):
    id: UUID4
    username: str | None = None
    admin: bool
    full_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class RecipeCommentCreate(MealieModel):
    recipe_id: UUID4
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RecipeCommentSave(RecipeCommentCreate):
    user_id: UUID4


class RecipeCommentUpdate(MealieModel):
    id: UUID4
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RecipeCommentOut(RecipeCommentCreate):
    id: UUID4
    recipe_id: UUID4
    created_at: datetime
    updated_at: datetime = UpdatedAtField(...)
    user_id: UUID4
    user: UserBase
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(RecipeComment.user),
            joinedload(RecipeComment.recipe).joinedload(RecipeModel.user),
        ]


class RecipeCommentPagination(PaginationBase):
    items: list[RecipeCommentOut]
