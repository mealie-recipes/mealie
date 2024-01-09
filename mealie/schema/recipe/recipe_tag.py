from typing import ClassVar

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class RecipeTag(MealieModel):
    id: UUID4 | None = None
    name: str
    slug: str

    _searchable_properties: ClassVar[list[str]] = ["name"]

    class Config:
        orm_mode = True
