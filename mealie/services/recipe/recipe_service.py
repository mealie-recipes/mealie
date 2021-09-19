from functools import cached_property
from pathlib import Path
from shutil import copytree, rmtree
from typing import Union

from fastapi import Depends, HTTPException, status

from mealie.core.dependencies.grouped import PublicDeps, UserDeps
from mealie.core.root_logger import get_logger
from mealie.db.data_access_layer.recipe_access_model import RecipeDataAccessModel
from mealie.schema.recipe.recipe import CreateRecipe, Recipe, RecipeSummary
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event
from mealie.services.recipe.mixins import recipe_creation_factory

logger = get_logger(module=__name__)


class RecipeService(CrudHttpMixins[CreateRecipe, Recipe, Recipe], UserHttpService[str, Recipe]):
    """
    Class Methods:
        `read_existing`: Reads an existing recipe from the database.
        `write_existing`: Updates an existing recipe in the database.
        `base`: Requires write permissions, but doesn't perform recipe checks
    """

    event_func = create_recipe_event

    @cached_property
    def dal(self) -> RecipeDataAccessModel:
        return self.db.recipes

    @classmethod
    def write_existing(cls, slug: str, deps: UserDeps = Depends()):
        return super().write_existing(slug, deps)

    @classmethod
    def read_existing(cls, slug: str, deps: PublicDeps = Depends()):
        return super().write_existing(slug, deps)

    def assert_existing(self, slug: str):
        self.populate_item(slug)
        if not self.item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not self.item.settings.public and not self.user:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    # CRUD METHODS
    def get_all(self, start=0, limit=None):
        return self.db.recipes.multi_query(
            {"group_id": self.user.group_id},
            start=start,
            limit=limit,
            override_schema=RecipeSummary,
        )

    def create_one(self, create_data: Union[Recipe, CreateRecipe]) -> Recipe:
        create_data = recipe_creation_factory(self.user, name=create_data.name, additional_attrs=create_data.dict())
        self._create_one(create_data, "RECIPE_ALREAD_EXISTS")
        self._create_event(
            "Recipe Created",
            f"'{self.item.name}' by {self.user.username} \n {self.settings.BASE_URL}/recipe/{self.item.slug}",
        )
        return self.item

    def update_one(self, update_data: Recipe) -> Recipe:
        original_slug = self.item.slug
        self._update_one(update_data, original_slug)
        self.check_assets(original_slug)
        return self.item

    def patch_one(self, patch_data: Recipe) -> Recipe:
        original_slug = self.item.slug
        self._patch_one(patch_data, original_slug)
        self.check_assets(original_slug)
        return self.item

    def delete_one(self) -> Recipe:
        self._delete_one(self.item.slug)
        self.delete_assets()
        self._create_event("Recipe Delete", f"'{self.item.name}' deleted by {self.user.full_name}")
        return self.item

    def check_assets(self, original_slug: str) -> None:
        """Checks if the recipe slug has changed, and if so moves the assets to a new file with the new slug."""
        if original_slug != self.item.slug:
            current_dir = self.app_dirs.RECIPE_DATA_DIR.joinpath(original_slug)

            try:
                copytree(current_dir, self.item.directory, dirs_exist_ok=True)
                logger.info(f"Renaming Recipe Directory: {original_slug} -> {self.item.slug}")
            except FileNotFoundError:
                logger.error(f"Recipe Directory not Found: {original_slug}")

        all_asset_files = [x.file_name for x in self.item.assets]

        for file in self.item.asset_dir.iterdir():
            file: Path
            if file.is_dir():
                continue
            if file.name not in all_asset_files:
                file.unlink()

    def delete_assets(self) -> None:
        recipe_dir = self.item.directory
        rmtree(recipe_dir, ignore_errors=True)
        logger.info(f"Recipe Directory Removed: {self.item.slug}")
