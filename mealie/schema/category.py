from typing import List, Optional

from fastapi_camelcase import CamelModel

from schema.recipe import Recipe


class CategoryBase(CamelModel):
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class RecipeCategoryResponse(CategoryBase):
    recipes: Optional[List[Recipe]]

    class Config:
        schema_extra = {"example": {"id": 1, "name": "dinner", "recipes": [{}]}}
