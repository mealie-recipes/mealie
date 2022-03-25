import enum

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe_category import CategoryBase, TagBase


class ExportTypes(str, enum.Enum):
    JSON = "json"


class ExportBase(MealieModel):
    recipes: list[str]


class ExportRecipes(ExportBase):
    export_type: ExportTypes = ExportTypes.JSON


class AssignCategories(ExportBase):
    categories: list[CategoryBase]


class AssignTags(ExportBase):
    tags: list[TagBase]


class DeleteRecipes(ExportBase):
    pass


class BulkActionError(MealieModel):
    recipe: str
    error: str


class BulkActionsResponse(MealieModel):
    success: bool
    message: str
    errors: list[BulkActionError] = []
