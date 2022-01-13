from functools import cached_property
from pathlib import Path

from fastapi import APIRouter, Depends

from mealie.core.dependencies.dependencies import temporary_zip_path
from mealie.core.security import create_file_token
from mealie.routes._base import BaseUserController, controller
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.recipe.recipe_bulk_actions import (
    AssignCategories,
    AssignTags,
    BulkActionsResponse,
    DeleteRecipes,
    ExportRecipes,
)
from mealie.schema.response.responses import SuccessResponse
from mealie.services.recipe.recipe_bulk_service import RecipeBulkActionsService

router = APIRouter(prefix="/bulk-actions", tags=["Recipe: Bulk Actions"])


@controller(router)
class RecipeBulkActionsController(BaseUserController):
    @cached_property
    def service(self) -> RecipeBulkActionsService:
        return RecipeBulkActionsService(self.repos, self.user, self.group)

    @router.post("/tag", response_model=BulkActionsResponse)
    def bulk_tag_recipes(self, tag_data: AssignTags):
        self.service.assign_tags(tag_data.recipes, tag_data.tags)

    @router.post("/categorize", response_model=BulkActionsResponse)
    def bulk_categorize_recipes(self, assign_cats: AssignCategories):
        self.service.assign_categories(assign_cats.recipes, assign_cats.categories)

    @router.post("/delete", response_model=BulkActionsResponse)
    def bulk_delete_recipes(self, delete_recipes: DeleteRecipes):
        self.service.delete_recipes(delete_recipes.recipes)

    @router.post("/export", status_code=202)
    def bulk_export_recipes(self, export_recipes: ExportRecipes, temp_path=Depends(temporary_zip_path)):
        self.service.export_recipes(temp_path, export_recipes.recipes)

    @router.get("/export/download")
    def get_exported_data_token(self, path: Path):
        """Returns a token to download a file"""

        return {"fileToken": create_file_token(path)}

    @router.get("/export", response_model=list[GroupDataExport])
    def get_exported_data(self):
        return self.service.get_exports()

    @router.delete("/export/purge", response_model=SuccessResponse)
    def purge_export_data(self):
        """Remove all exports data, including items on disk without database entry"""
        amountDelete = self.service.purge_exports()
        return SuccessResponse.respond(f"{amountDelete} exports deleted")
