import enum

from pydantic import UUID4, Field, field_validator

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe_category import CategoryBase, TagBase
from mealie.schema.recipe.recipe_settings import RecipeSettings


class ExportTypes(enum.StrEnum):
    JSON = "json"


class ExportBase(MealieModel):
    recipes: list[str]


class ExportRecipes(ExportBase):
    export_type: ExportTypes = ExportTypes.JSON


class AssignCategories(ExportBase):
    categories: list[CategoryBase]


class AssignTags(ExportBase):
    tags: list[TagBase]


class AssignSettings(ExportBase):
    settings: RecipeSettings


class DeleteRecipes(ExportBase):
    pass


class OrganizerOperation(enum.StrEnum):
    ADD = "add"
    REMOVE = "remove"


class BulkOrganizeRecipes(MealieModel):
    recipes: list[UUID4] = Field(min_length=1)
    operation: OrganizerOperation
    tags: list[TagBase] = []
    categories: list[CategoryBase] = []

    @field_validator("recipes")
    @classmethod
    def recipes_are_unique(cls, recipes: list[UUID4]) -> list[UUID4]:
        if len(recipes) != len(set(recipes)):
            raise ValueError("recipes must not contain duplicate IDs")
        return recipes

    @field_validator("tags", "categories")
    @classmethod
    def organizers_are_unique(cls, organizers: list[TagBase | CategoryBase]) -> list[TagBase | CategoryBase]:
        seen: set[UUID4] = set()
        unique: list[TagBase | CategoryBase] = []
        for organizer in organizers:
            if organizer.id not in seen:
                seen.add(organizer.id)
                unique.append(organizer)
        return unique
