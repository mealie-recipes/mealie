from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class UserBase(MealieModel):
    id: int
    username: Optional[str]
    admin: bool

    class Config:
        orm_mode = True


class RecipeCommentCreate(MealieModel):
    recipe_id: UUID4
    text: str


class RecipeCommentSave(RecipeCommentCreate):
    user_id: UUID4


class RecipeCommentUpdate(MealieModel):
    id: UUID
    text: str


class RecipeCommentOut(RecipeCommentCreate):
    id: UUID
    recipe_id: UUID4
    created_at: datetime
    update_at: datetime
    user_id: UUID4
    user: UserBase

    class Config:
        orm_mode = True
