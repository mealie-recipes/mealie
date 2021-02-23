from typing import List, Optional

from pydantic.main import BaseModel
from services.recipe_services import Recipe


class RecipeCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    recipes: Optional[List[Recipe]]

    class Config:
        schema_extra = {"example": {"id": 1, "name": "dinner", "recipes": [{}]}}
