import json
import shutil
from functools import cached_property
from pathlib import Path
from shutil import copytree, rmtree
from typing import Union
from zipfile import ZipFile

from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy import exc

from mealie.core.dependencies.grouped import UserDeps
from mealie.core.root_logger import get_logger
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.recipe.recipe import CreateRecipe, Recipe, RecipeSummary
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event
from mealie.services.image.image import write_image
from mealie.services.recipe.mixins import recipe_creation_factory

from .template_service import TemplateService

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
    def exception_key(self) -> dict:
        return {exc.IntegrityError: self.t("recipe.unique-name-error")}

    @cached_property
    def repo(self) -> RepositoryRecipes:
        return self.db.recipes.by_group(self.group_id)

    @classmethod
    def write_existing(cls, slug: str, deps: UserDeps = Depends()):
        return super().write_existing(slug, deps)

    @classmethod
    def read_existing(cls, slug: str, deps: UserDeps = Depends()):
        return super().write_existing(slug, deps)

    def assert_existing(self, slug: str):
        self.populate_item(slug)
        if not self.item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not self.item.settings.public and not self.user:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    def can_update(self) -> bool:
        if self.item.settings.locked and self.user.id != self.item.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        return True

    def get_all(self, start=0, limit=None, load_foods=False) -> list[RecipeSummary]:
        items = self.db.recipes.summary(self.user.group_id, start=start, limit=limit, load_foods=load_foods)

        new_items = []

        for item in items:
            # Pydantic/FastAPI can't seem to serialize the ingredient field on thier own.
            new_item = item.__dict__

            if load_foods:
                new_item["recipe_ingredient"] = [x.__dict__ for x in item.recipe_ingredient]

            new_items.append(new_item)

        return [RecipeSummary.construct(**x) for x in new_items]

    def create_one(self, create_data: Union[Recipe, CreateRecipe]) -> Recipe:
        group = self.db.groups.get(self.group_id, "id")

        create_data: Recipe = recipe_creation_factory(
            self.user,
            name=create_data.name,
            additional_attrs=create_data.dict(),
        )

        create_data.settings = RecipeSettings(
            public=group.preferences.recipe_public,
            show_nutrition=group.preferences.recipe_show_nutrition,
            show_assets=group.preferences.recipe_show_assets,
            landscape_view=group.preferences.recipe_landscape_view,
            disable_comments=group.preferences.recipe_disable_comments,
            disable_amount=group.preferences.recipe_disable_amount,
        )

        self._create_one(create_data, self.t("generic.server-error"), self.exception_key)

        self._create_event(
            "Recipe Created",
            f"'{self.item.name}' by {self.user.username} \n {self.settings.BASE_URL}/recipe/{self.item.slug}",
        )
        return self.item

    def create_from_zip(self, archive: UploadFile, temp_path: Path) -> Recipe:
        """
        `create_from_zip` creates a recipe in the database from a zip file exported from Mealie. This is NOT
        a generic import from a zip file.
        """
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(archive.file, buffer)

        recipe_dict = None
        recipe_image = None

        with ZipFile(temp_path) as myzip:
            for file in myzip.namelist():
                if file.endswith(".json"):
                    with myzip.open(file) as myfile:
                        recipe_dict = json.loads(myfile.read())
                elif file.endswith(".webp"):
                    with myzip.open(file) as myfile:
                        recipe_image = myfile.read()

        self.create_one(Recipe(**recipe_dict))

        if self.item:
            write_image(self.item.slug, recipe_image, "webp")

        return self.item

    def update_one(self, update_data: Recipe) -> Recipe:
        self.can_update()

        if self.item.settings.locked != update_data.settings.locked and self.item.user_id != self.user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        original_slug = self.item.slug
        self._update_one(update_data, original_slug)

        self.check_assets(original_slug)
        return self.item

    def patch_one(self, patch_data: Recipe) -> Recipe:
        self.can_update()

        original_slug = self.item.slug
        self._patch_one(patch_data, original_slug)

        self.check_assets(original_slug)
        return self.item

    def delete_one(self) -> Recipe:
        self.can_update()
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

    # =================================================================
    # Recipe Template Methods

    def render_template(self, temp_dir: Path, template: str = None) -> Path:
        t_service = TemplateService(temp_dir)
        return t_service.render(self.item, template)
