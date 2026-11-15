import enum

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe_settings import RecipeSettings

from .recipe_organizers import CategoryDraft, TagDraft


class ExportTypes(enum.StrEnum):
    JSON = "json"


class ExportBase(MealieModel):
    recipes: list[str]


class ExportRecipes(ExportBase):
    export_type: ExportTypes = ExportTypes.JSON


class AssignCategories(ExportBase):
    categories: list[CategoryDraft]


class AssignTags(ExportBase):
    tags: list[TagDraft]


class AssignSettings(ExportBase):
    settings: RecipeSettings


class DeleteRecipes(ExportBase):
    pass
