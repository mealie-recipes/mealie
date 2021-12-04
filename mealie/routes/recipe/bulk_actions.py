from pathlib import Path

from fastapi import APIRouter, Depends

from mealie.core.dependencies.dependencies import temporary_zip_path
from mealie.core.security import create_file_token
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.recipe.recipe_bulk_actions import (
    AssignCategories,
    AssignTags,
    BulkActionsResponse,
    DeleteRecipes,
    ExportRecipes,
)
from mealie.services.recipe.recipe_bulk_service import RecipeBulkActions

router = APIRouter(prefix="/bulk-actions")


@router.post("/tag", response_model=BulkActionsResponse)
def bulk_tag_recipes(
    tag_data: AssignTags,
    bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private),
):
    bulk_service.assign_tags(tag_data.recipes, tag_data.tags)


@router.post("/categorize", response_model=BulkActionsResponse)
def bulk_categorize_recipes(
    assign_cats: AssignCategories,
    bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private),
):
    bulk_service.assign_categories(assign_cats.recipes, assign_cats.categories)


@router.post("/delete", response_model=BulkActionsResponse)
def bulk_delete_recipes(
    delete_recipes: DeleteRecipes,
    bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private),
):
    bulk_service.delete_recipes(delete_recipes.recipes)


export_router = APIRouter(prefix="/bulk-actions")


@export_router.post("/export")
def bulk_export_recipes(
    export_recipes: ExportRecipes,
    temp_path=Depends(temporary_zip_path),
    bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private),
):
    bulk_service.export_recipes(temp_path, export_recipes.recipes)

    # return FileResponse(temp_path, filename="recipes.zip")


@export_router.get("/export/download")
def get_exported_data_token(path: Path, _: RecipeBulkActions = Depends(RecipeBulkActions.private)):
    # return FileResponse(temp_path, filename="recipes.zip")
    """Returns a token to download a file"""

    return {"fileToken": create_file_token(path)}


@export_router.get("/export", response_model=list[GroupDataExport])
def get_exported_data(bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private)):
    return bulk_service.get_exports()

    # return FileResponse(temp_path, filename="recipes.zip")


@export_router.delete("/export/purge")
def purge_export_data(bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private)):
    """Remove all exports data, including items on disk without database entry"""
    amountDelete = bulk_service.purge_exports()
    return {"message": f"{amountDelete} exports deleted"}
