from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from mealie.core.dependencies.dependencies import temporary_zip_path
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


@router.post("/export", response_class=FileResponse)
def bulk_export_recipes(
    export_recipes: ExportRecipes,
    temp_path=Depends(temporary_zip_path),
    bulk_service: RecipeBulkActions = Depends(RecipeBulkActions.private),
):
    bulk_service.export_recipes(temp_path, export_recipes.recipes)

    return FileResponse(temp_path, filename="recipes.zip")
