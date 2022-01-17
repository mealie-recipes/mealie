import enum

from fastapi_camelcase import CamelModel

from mealie.schema.recipe.recipe_category import CategoryBase, TagBase


class ExportTypes(str, enum.Enum):
    JSON = "json"


class ExportBase(CamelModel):
    recipes: list[str]


class ExportRecipes(ExportBase):
    export_type: ExportTypes = ExportTypes.JSON


class AssignCategories(ExportBase):
    categories: list[CategoryBase]


class AssignTags(ExportBase):
    tags: list[TagBase]


class DeleteRecipes(ExportBase):
    pass


class BulkActionError(CamelModel):
    recipe: str
    error: str


class BulkActionsResponse(CamelModel):
    success: bool
    message: str
    errors: list[BulkActionError] = []
