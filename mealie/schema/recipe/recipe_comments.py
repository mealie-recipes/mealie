from datetime import datetime

from pydantic import UUID4
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeComment
from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class UserBase(MealieModel):
    id: UUID4
    username: str | None
    admin: bool

    class Config:
        orm_mode = True


class RecipeCommentCreate(MealieModel):
    recipe_id: UUID4
    text: str


class RecipeCommentSave(RecipeCommentCreate):
    user_id: UUID4


class RecipeCommentUpdate(MealieModel):
    id: UUID4
    text: str


class RecipeCommentOut(RecipeCommentCreate):
    id: UUID4
    recipe_id: UUID4
    created_at: datetime
    update_at: datetime
    user_id: UUID4
    user: UserBase

    class Config:
        orm_mode = True

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(RecipeComment.user)]


class RecipeCommentPagination(PaginationBase):
    items: list[RecipeCommentOut]
