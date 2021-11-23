from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_camelcase import CamelModel


class UserBase(CamelModel):
    id: int
    username: Optional[str]
    admin: bool

    class Config:
        orm_mode = True


class RecipeCommentCreate(CamelModel):
    recipe_id: int
    text: str


class RecipeCommentSave(RecipeCommentCreate):
    user_id: int


class RecipeCommentUpdate(CamelModel):
    id: UUID
    text: str


class RecipeCommentOut(RecipeCommentCreate):
    id: UUID
    recipe_id: int
    created_at: datetime
    update_at: datetime
    user_id: int
    user: UserBase

    class Config:
        orm_mode = True
