from pydantic import UUID4, ConfigDict, field_validator
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeModel, Tool
from mealie.schema._mealie import MealieModel


class RecipeToolCreate(MealieModel):
    name: str
    households_with_tool: list[str] = []


class RecipeToolSave(RecipeToolCreate):
    group_id: UUID4


class RecipeToolOut(RecipeToolCreate):
    id: UUID4
    slug: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("households_with_tool", mode="before")
    def convert_households_to_slugs(cls, v):
        if not v:
            return []

        try:
            return [household.slug for household in v]
        except AttributeError:
            return v

    def is_on_hand(self, household_slug: str) -> bool:
        return household_slug in self.households_with_tool

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tool.households_with_tool),
        ]


class RecipeToolResponse(RecipeToolOut):
    recipes: list["RecipeSummary"] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tool.households_with_tool),
            selectinload(Tool.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tool.recipes).joinedload(RecipeModel.tags),
            selectinload(Tool.recipes).joinedload(RecipeModel.tools),
        ]


from .recipe import RecipeSummary  # noqa: E402

RecipeToolResponse.model_rebuild()
