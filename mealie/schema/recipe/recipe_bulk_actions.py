import enum

from fastapi_camelcase import CamelModel

from mealie.schema.recipe.recipe_category import CategoryBase, TagBase


class ExportTypes(str, enum.Enum):
    JSON = "json"


class _ExportBase(CamelModel):
    recipes: list[str]


class ExportRecipes(_ExportBase):
    export_type: ExportTypes = ExportTypes.JSON


class AssignCategories(_ExportBase):
    categories: list[CategoryBase]


class AssignTags(_ExportBase):
    tags: list[TagBase]


class DeleteRecipes(_ExportBase):
    pass


class BulkActionError(CamelModel):
    recipe: str
    error: str


class BulkActionsResponse(CamelModel):
    success: bool
    message: str
    errors: list[BulkActionError] = []
