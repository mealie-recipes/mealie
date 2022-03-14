import typing

from fastapi_camelcase import CamelModel
from pydantic import UUID4


class RecipeToolCreate(CamelModel):
    name: str
    on_hand: bool = False


class RecipeToolSave(RecipeToolCreate):
    group_id: UUID4


class RecipeTool(RecipeToolCreate):
    id: UUID4
    slug: str

    class Config:
        orm_mode = True


class RecipeToolResponse(RecipeTool):
    recipes: typing.List["Recipe"] = []

    class Config:
        orm_mode = True


from .recipe import Recipe

RecipeToolResponse.update_forward_refs()
