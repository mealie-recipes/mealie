import enum

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
