from pathlib import Path
from shutil import copytree, rmtree
from typing import Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from mealie.core.dependencies.grouped import ReadDeps, WriteDeps
from mealie.core.root_logger import get_logger
from mealie.schema.recipe.recipe import CreateRecipe, Recipe
from mealie.services.base_http_service.base_http_service import BaseHttpService
from mealie.services.events import create_recipe_event

logger = get_logger(module=__name__)


class RecipeService(BaseHttpService[str, str]):
    """
    Class Methods:
        `read_existing`: Reads an existing recipe from the database.
        `write_existing`: Updates an existing recipe in the database.
        `base`: Requires write permissions, but doesn't perform recipe checks
    """

    event_func = create_recipe_event
    recipe: Recipe  # Required for proper type hints

    @classmethod
    def write_existing(cls, slug: str, deps: WriteDeps = Depends()):
        return super().write_existing(slug, deps)

    @classmethod
    def read_existing(cls, slug: str, deps: ReadDeps = Depends()):
        return super().write_existing(slug, deps)

    def assert_existing(self, slug: str):
        self.pupulate_recipe(slug)

        if not self.recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not self.recipe.settings.public and not self.user:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    def pupulate_recipe(self, slug: str) -> Recipe:
        self.recipe = self.db.recipes.get(self.session, slug)
        return self.recipe

    # CRUD METHODS
    def create_recipe(self, create_data: Union[Recipe, CreateRecipe]) -> Recipe:
        if isinstance(create_data, CreateRecipe):
            create_data = Recipe(name=create_data.name)

        try:
            self.recipe = self.db.recipes.create(self.session, create_data)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._create_event(
            "Recipe Created (URL)",
            f"'{self.recipe.name}' by {self.user.username} \n {self.settings.BASE_URL}/recipe/{self.recipe.slug}",
        )

        return self.recipe

    def update_recipe(self, update_data: Recipe) -> Recipe:
        original_slug = self.recipe.slug

        try:
            self.recipe = self.db.recipes.update(self.session, original_slug, update_data)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._check_assets(original_slug)

        return self.recipe

    def patch_recipe(self, patch_data: Recipe) -> Recipe:
        original_slug = self.recipe.slug

        try:
            self.recipe = self.db.recipes.patch(
                self.session, original_slug, patch_data.dict(exclude_unset=True, exclude_defaults=True)
            )
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._check_assets(original_slug)

        return self.recipe

    def delete_recipe(self) -> Recipe:
        """removes a recipe from the database and purges the existing files from the filesystem.

        Raises:
            HTTPException: 400 Bad Request

        Returns:
            Recipe: The deleted recipe
        """

        try:
            recipe: Recipe = self.db.recipes.delete(self.session, self.recipe.slug)
            self._delete_assets()
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        self._create_event("Recipe Delete", f"'{recipe.name}' deleted by {self.user.full_name}")
        return recipe

    def _check_assets(self, original_slug: str) -> None:
        """Checks if the recipe slug has changed, and if so moves the assets to a new file with the new slug."""
        if original_slug != self.recipe.slug:
            current_dir = self.app_dirs.RECIPE_DATA_DIR.joinpath(original_slug)

            try:
                copytree(current_dir, self.recipe.directory, dirs_exist_ok=True)
                logger.info(f"Renaming Recipe Directory: {original_slug} -> {self.recipe.slug}")
            except FileNotFoundError:
                logger.error(f"Recipe Directory not Found: {original_slug}")

        all_asset_files = [x.file_name for x in self.recipe.assets]

        for file in self.recipe.asset_dir.iterdir():
            file: Path
            if file.is_dir():
                continue
            if file.name not in all_asset_files:
                file.unlink()

    def _delete_assets(self) -> None:
        recipe_dir = self.recipe.directory
        rmtree(recipe_dir, ignore_errors=True)
        logger.info(f"Recipe Directory Removed: {self.recipe.slug}")
