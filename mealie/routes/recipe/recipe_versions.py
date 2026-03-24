from functools import cached_property

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.recipe._base import BaseRecipeController
from mealie.schema.recipe.recipe_version import (
    RecipeDiff,
    RecipeVersionOut,
    RecipeVersionPagination,
    RecipeVersionSummary,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.recipe.recipe_version_service import RecipeVersionService

router = UserAPIRouter()


@controller(router)
class RecipeVersionController(BaseRecipeController):
    @cached_property
    def version_service(self) -> RecipeVersionService:
        return RecipeVersionService(self.repos)

    @router.get("/{slug}/versions", response_model=list[RecipeVersionSummary])
    def get_recipe_versions(self, slug: str):
        """List all versions for a recipe."""
        recipe = self.group_recipes.get_by_slug(self.group_id, slug)
        if not recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")
        return self.version_service.get_versions(recipe.id)

    @router.get("/{slug}/versions/{version_id}", response_model=RecipeVersionOut)
    def get_recipe_version(self, slug: str, version_id: UUID4):
        """Get a single version with its full snapshot."""
        version = self.version_service.get_version(version_id)
        if not version:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Version not found")
        return version

    @router.get("/{slug}/versions/{version_id}/diff", response_model=RecipeDiff)
    def get_recipe_version_diff(self, slug: str, version_id: UUID4, compare_to: str = Query(default="current")):
        """Compute diff between a version and another version or current state.

        compare_to: "current" (default) or a version_id UUID.
        """
        recipe = self.group_recipes.get_by_slug(self.group_id, slug)
        if not recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")

        diff = self.version_service.compute_diff(version_id, compare_to, current_recipe=recipe)
        if not diff:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Version not found or comparison failed")
        return diff

    @router.post("/{slug}/versions/{version_id}/restore", response_model=RecipeVersionOut)
    def restore_recipe_version(self, slug: str, version_id: UUID4):
        """Restore a recipe to a previous version.

        This creates a new version snapshot (of current state) then applies the old version's data.
        """
        import json

        from mealie.schema.recipe.recipe import Recipe

        recipe = self.group_recipes.get_by_slug(self.group_id, slug)
        if not recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")

        if not self.service.can_update([recipe.slug]):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this recipe")

        version = self.version_service.get_version(version_id)
        if not version:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Version not found")

        # Parse the snapshot and apply it as an update
        snapshot_data = json.loads(version.snapshot)

        # Merge snapshot data into current recipe (keeps id, slug, group_id, user_id, etc.)
        update_data = recipe.model_dump()
        update_data.update(snapshot_data)
        update_recipe = Recipe(**update_data)

        # update_one will create a new version snapshot before applying the restore
        self.service.update_one(recipe.slug, update_recipe)

        return version
