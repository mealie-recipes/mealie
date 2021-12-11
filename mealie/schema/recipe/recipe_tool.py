from typing import List

from fastapi_camelcase import CamelModel


class RecipeToolCreate(CamelModel):
    name: str
    on_hand: bool = False


class RecipeTool(RecipeToolCreate):
    id: int
    slug: str

    class Config:
        orm_mode = True


class RecipeToolResponse(RecipeTool):
    recipes: List["Recipe"] = []

    class Config:
        orm_mode = True


from .recipe import Recipe

RecipeToolResponse.update_forward_refs()
