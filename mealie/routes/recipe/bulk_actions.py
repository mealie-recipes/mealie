from functools import cached_property
from pathlib import Path

from fastapi import APIRouter, HTTPException

from mealie.core.dependencies.dependencies import get_temporary_zip_path
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
from mealie.schema.response.responses import SuccessResponse
from mealie.services.recipe.recipe_bulk_service import RecipeBulkActionsService

router = APIRouter(prefix="/bulk-actions")


@controller(router)
class RecipeBulkActionsController(BaseUserController):
    @cached_property
    def service(self) -> RecipeBulkActionsService:
        return RecipeBulkActionsService(self.repos, self.user, self.group)

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
        self.service.delete_recipes(delete_recipes.recipes)

    @router.post("/export", status_code=202)
    def bulk_export_recipes(self, export_recipes: ExportRecipes):
        with get_temporary_zip_path() as temp_path:
            self.service.export_recipes(temp_path, export_recipes.recipes)

    @router.get("/export/download")
    def get_exported_data_token(self, path: Path):
        """Returns a token to download a file"""
        path = Path(path).resolve()

        if not path.is_relative_to(self.folders.DATA_DIR):
            raise HTTPException(400, "path must be relative to data directory")

        return {"fileToken": create_file_token(path)}

    @router.get("/export", response_model=list[GroupDataExport])
    def get_exported_data(self):
        return self.service.get_exports()

    @router.delete("/export/purge", response_model=SuccessResponse)
    def purge_export_data(self):
        """Remove all exports data, including items on disk without database entry"""
        amountDelete = self.service.purge_exports()
        return SuccessResponse.respond(f"{amountDelete} exports deleted")
