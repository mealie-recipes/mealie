from datetime import datetime
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic.utils import GetterDict


class UserBase(CamelModel):
    id: int
    username: Optional[str]
    admin: bool

    class Config:
        orm_mode = True


class CreateComment(CamelModel):
    text: str


class SaveComment(CreateComment):
    recipe_slug: str
    user: int

    class Config:
        orm_mode = True


class CommentOut(CreateComment):
    id: int
    uuid: str
    recipe_slug: str
    date_added: datetime
    user: UserBase

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm):
            return {
                **GetterDict(name_orm),
                "recipe_slug": name_orm.recipe.slug,
            }
