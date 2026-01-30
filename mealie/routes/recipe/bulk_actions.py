from functools import cached_property
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4

from mealie.core.dependencies.dependencies import get_temporary_zip_path
from mealie.core.exceptions import PermissionDenied
from mealie.core.security import create_file_token
from mealie.routes._base import BaseUserController, controller
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.recipe.recipe_bulk_actions import (
    AssignCategories,
    AssignSettings,
    AssignTags,
    DeleteRecipes,
    ExportRecipes,
)
from mealie.schema.response.responses import ErrorResponse, SuccessResponse
from mealie.services.recipe.recipe_bulk_service import RecipeBulkActionsService
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter(prefix="/bulk-actions")


@controller(router)
class RecipeBulkActionsController(BaseUserController):
    @cached_property
    def service(self) -> RecipeBulkActionsService:
        return RecipeBulkActionsService(self.repos, self.user, self.group)

    @cached_property
    def recipe_service(self) -> RecipeService:
        return RecipeService(self.repos, self.user, self.household, self.translator)

    # TODO Should these actions return some success response?
    @router.post("/tag")
    def bulk_tag_recipes(self, tag_data: AssignTags):
        self.service.assign_tags(tag_data.recipes, tag_data.tags)

    @router.post("/settings")
    def bulk_settings_recipes(self, settings_data: AssignSettings):
        self.service.set_settings(settings_data.recipes, settings_data.settings)

    @router.post("/categorize")
    def bulk_categorize_recipes(self, assign_cats: AssignCategories):
        self.service.assign_categories(assign_cats.recipes, assign_cats.categories)

    @router.post("/delete")
    def bulk_delete_recipes(self, delete_recipes: DeleteRecipes):
        # TODO: this route should be migrated to the standard recipe controller
        try:
            self.recipe_service.delete_many(delete_recipes.recipes)
        except PermissionDenied as e:
            self.logger.error("Permission Denied on recipe controller action")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=ErrorResponse.respond(message="Permission Denied")
            ) from e

    @router.post("/export", status_code=202)
    def bulk_export_recipes(self, export_recipes: ExportRecipes):
        with get_temporary_zip_path() as temp_path:
            self.service.export_recipes(temp_path, export_recipes.recipes)

    @router.get("/export/{export_id}/download")
    def get_exported_data_token(self, export_id: UUID4):
        """Returns a token to download a file"""

        export = self.service.get_export(export_id)
        if not export:
            raise HTTPException(404, "export not found")

        path = Path(export.path).resolve()
        return {"fileToken": create_file_token(path)}

    @router.get("/export", response_model=list[GroupDataExport])
    def get_exported_data(self):
        return self.service.get_exports()

    @router.delete("/export/purge", response_model=SuccessResponse)
    def purge_export_data(self):
        """Remove all exports data, including items on disk without database entry"""
        amountDelete = self.service.purge_exports()
        return SuccessResponse.respond(f"{amountDelete} exports deleted")
