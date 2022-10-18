import typing

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class RecipeToolCreate(MealieModel):
    name: str
    on_hand: bool = False


class RecipeToolSave(RecipeToolCreate):
    group_id: UUID4


class RecipeToolOut(RecipeToolCreate):
    id: UUID4
    slug: str

    class Config:
        orm_mode = True


class RecipeToolResponse(RecipeToolOut):
    recipes: typing.List["Recipe"] = []

    class Config:
        orm_mode = True


from .recipe import Recipe  # noqa: E402

RecipeToolResponse.update_forward_refs()
