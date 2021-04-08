from typing import List, Optional

from fastapi_camelcase import CamelModel
from mealie.schema.recipe import Recipe


class CategoryIn(CamelModel):
    name: str


class CategoryBase(CategoryIn):
    id: int
    slug: str

    class Config:
        orm_mode = True


class RecipeCategoryResponse(CategoryBase):
    recipes: Optional[List[Recipe]]

    class Config:
        schema_extra = {"example": {"id": 1, "name": "dinner", "recipes": [{}]}}


class TagIn(CategoryIn):
    pass


class TagBase(CategoryBase):
    pass


class RecipeTagResponse(RecipeCategoryResponse):
    pass
