import json
import shutil
from datetime import datetime
from pathlib import Path
from shutil import copytree, rmtree
from typing import Any
from uuid import UUID, uuid4
from zipfile import ZipFile

from fastapi import UploadFile
from slugify import slugify

from mealie.core import exceptions
from mealie.pkgs import cache
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_generic import RepositoryGeneric
from mealie.schema.recipe.recipe import CreateRecipe, Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventCreate, TimelineEventType
from mealie.schema.recipe.request_helpers import RecipeDuplicate
from mealie.schema.user.user import GroupInDB, PrivateUser, UserRatingCreate
from mealie.services._base_service import BaseService
from mealie.services.recipe.recipe_data_service import RecipeDataService

from .template_service import TemplateService

step_text = """Recipe steps as well as other fields in the recipe page support markdown syntax.

**Add a link**

[My Link](https://demo.mealie.io)

"""

ingredient_note = "1 Cup Flour"


class RecipeService(BaseService):
    def __init__(self, repos: AllRepositories, user: PrivateUser, group: GroupInDB):
        self.repos = repos
        self.user = user
        self.group = group
        super().__init__()

    def _get_recipe(self, data: str | UUID, key: str | None = None) -> Recipe:
        recipe = self.repos.recipes.by_group(self.group.id).get_one(data, key)
        if recipe is None:
            raise exceptions.NoEntryFound("Recipe not found.")
        return recipe

    def can_update(self, recipe: Recipe) -> bool:
        if recipe.settings is None:
            raise exceptions.UnexpectedNone("Recipe Settings is None")
        return recipe.settings.locked is False or self.user.id == recipe.user_id

    def can_lock_unlock(self, recipe: Recipe) -> bool:
        return recipe.user_id == self.user.id

    def check_assets(self, recipe: Recipe, original_slug: str) -> None:
        """Checks if the recipe slug has changed, and if so moves the assets to a new file with the new slug."""
        if original_slug != recipe.slug:
            current_dir = self.directories.RECIPE_DATA_DIR.joinpath(original_slug)

            try:
                copytree(current_dir, recipe.directory, dirs_exist_ok=True)
                self.logger.debug(f"Renaming Recipe Directory: {original_slug} -> {recipe.slug}")
            except FileNotFoundError:
                self.logger.error(f"Recipe Directory not Found: {original_slug}")

        if recipe.assets is None:
            recipe.assets = []

        all_asset_files = [x.file_name for x in recipe.assets]

        for file in recipe.asset_dir.iterdir():
            if file.is_dir():
                continue
            if file.name not in all_asset_files:
                file.unlink()

    def delete_assets(self, recipe: Recipe) -> None:
        recipe_dir = recipe.directory
        rmtree(recipe_dir, ignore_errors=True)
        self.logger.info(f"Recipe Directory Removed: {recipe.slug}")

    @staticmethod
    def _recipe_creation_factory(user: PrivateUser, name: str, additional_attrs: dict | None = None) -> Recipe:
        """
        The main creation point for recipes. The factor method returns an instance of the
        Recipe Schema class with the appropriate defaults set. Recipes should not be created
        elsewhere to avoid conflicts.
        """
        additional_attrs = additional_attrs or {}
        additional_attrs["name"] = name
        additional_attrs["user_id"] = user.id
        additional_attrs["group_id"] = user.group_id

        if additional_attrs.get("tags"):
            for i in range(len(additional_attrs.get("tags", []))):
                additional_attrs["tags"][i]["group_id"] = user.group_id

        if not additional_attrs.get("recipe_ingredient"):
            additional_attrs["recipe_ingredient"] = [RecipeIngredient(note=ingredient_note)]

        if not additional_attrs.get("recipe_instructions"):
            additional_attrs["recipe_instructions"] = [RecipeStep(text=step_text)]

        return Recipe(**additional_attrs)

    def get_one_by_slug_or_id(self, slug_or_id: str | UUID) -> Recipe | None:
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            return self._get_recipe(slug_or_id, "id")

        else:
            return self._get_recipe(slug_or_id, "slug")

    def create_one(self, create_data: Recipe | CreateRecipe) -> Recipe:
        if create_data.name is None:
            create_data.name = "New Recipe"

        data: Recipe = self._recipe_creation_factory(
            self.user,
            name=create_data.name,
            additional_attrs=create_data.model_dump(),
        )

        if isinstance(create_data, CreateRecipe) or create_data.settings is None:
            if self.group.preferences is not None:
                data.settings = RecipeSettings(
                    public=self.group.preferences.recipe_public,
                    show_nutrition=self.group.preferences.recipe_show_nutrition,
                    show_assets=self.group.preferences.recipe_show_assets,
                    landscape_view=self.group.preferences.recipe_landscape_view,
                    disable_comments=self.group.preferences.recipe_disable_comments,
                    disable_amount=self.group.preferences.recipe_disable_amount,
                )
            else:
                data.settings = RecipeSettings()

        rating_input = data.rating
        new_recipe = self.repos.recipes.create(data)

        # convert rating into user rating
        if rating_input:
            self.repos.user_ratings.create(
                UserRatingCreate(
                    user_id=self.user.id,
                    recipe_id=new_recipe.id,
                    rating=rating_input,
                    is_favorite=False,
                )
            )

        # create first timeline entry
        timeline_event_data = RecipeTimelineEventCreate(
            user_id=new_recipe.user_id,
            recipe_id=new_recipe.id,
            subject="Recipe Created",
            event_type=TimelineEventType.system,
            timestamp=new_recipe.created_at or datetime.now(),
        )

        self.repos.recipe_timeline_events.create(timeline_event_data)
        return new_recipe

    def _transform_user_id(self, user_id: str) -> str:
        query = self.repos.users.by_group(self.group.id).get_one(user_id)
        if query:
            return user_id
        else:
            # default to the current user
            return str(self.user.id)

    def _transform_category_or_tag(self, data: dict, repo: RepositoryGeneric) -> dict:
        slug = data.get("slug")
        if not slug:
            return data

        # if the item exists, return the actual data
        query = repo.get_one(slug, "slug")
        if query:
            return query.model_dump()

        # otherwise, create the item
        new_item = repo.create(data)
        return new_item.model_dump()

    def _process_recipe_data(self, key: str, data: list | dict | Any):
        if isinstance(data, list):
            return [self._process_recipe_data(key, item) for item in data]

        elif isinstance(data, str):
            # make sure the user is valid
            if key == "user_id":
                return self._transform_user_id(str(data))

            return data

        elif not isinstance(data, dict):
            return data

        # force group_id to match the group id of the current user
        data["group_id"] = str(self.group.id)

        # make sure categories and tags are valid
        if key == "recipe_category":
            return self._transform_category_or_tag(data, self.repos.categories.by_group(self.group.id))
        elif key == "tags":
            return self._transform_category_or_tag(data, self.repos.tags.by_group(self.group.id))

        # recursively process other objects
        for k, v in data.items():
            data[k] = self._process_recipe_data(k, v)

        return data

    def clean_recipe_dict(self, recipe: dict[str, Any]) -> dict[str, Any]:
        return self._process_recipe_data("recipe", recipe)

    def create_from_zip(self, archive: UploadFile, temp_path: Path) -> Recipe:
        """
        `create_from_zip` creates a recipe in the database from a zip file exported from Mealie. This is NOT
        a generic import from a zip file.
        """
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(archive.file, buffer)

        recipe_dict: dict | None = None
        recipe_image: bytes | None = None

        with ZipFile(temp_path) as myzip:
            for file in myzip.namelist():
                if file.endswith(".json"):
                    with myzip.open(file) as myfile:
                        recipe_dict = json.loads(myfile.read())
                elif file.endswith(".webp"):
                    with myzip.open(file) as myfile:
                        recipe_image = myfile.read()

        if recipe_dict is None:
            raise exceptions.UnexpectedNone("No json data found in Zip")

        recipe = self.create_one(Recipe(**self.clean_recipe_dict(recipe_dict)))

        if recipe and recipe.id:
            data_service = RecipeDataService(recipe.id)

        if recipe_image:
            data_service.write_image(recipe_image, "webp")

        return recipe

    def duplicate_one(self, old_slug: str, dup_data: RecipeDuplicate) -> Recipe:
        """Duplicates a recipe and returns the new recipe."""

        old_recipe = self._get_recipe(old_slug)
        new_recipe_data = old_recipe.model_dump(exclude={"id", "name", "slug", "image", "comments"}, round_trip=True)
        new_recipe = Recipe.model_validate(new_recipe_data)

        # Asset images in steps directly link to the original recipe, so we
        # need to update them to references to the assets we copy below
        def replace_recipe_step(step: RecipeStep) -> RecipeStep:
            new_id = uuid4()
            new_text = step.text.replace(str(old_recipe.id), str(new_recipe.id))
            new_step = step.model_copy(update={"id": new_id, "text": new_text})
            return new_step

        # Copy ingredients to make them independent of the original
        def copy_recipe_ingredient(ingredient: RecipeIngredient):
            new_reference_id = uuid4()
            new_ingredient = ingredient.model_copy(update={"reference_id": new_reference_id})
            return new_ingredient

        new_name = dup_data.name if dup_data.name else old_recipe.name or ""
        new_recipe.id = uuid4()
        new_recipe.slug = slugify(new_name)
        new_recipe.image = cache.cache_key.new_key() if old_recipe.image else None
        new_recipe.recipe_instructions = (
            None
            if old_recipe.recipe_instructions is None
            else list(map(replace_recipe_step, old_recipe.recipe_instructions))
        )
        new_recipe.recipe_ingredient = (
            None
            if old_recipe.recipe_ingredient is None
            else list(map(copy_recipe_ingredient, old_recipe.recipe_ingredient))
        )

        new_recipe = self._recipe_creation_factory(
            self.user,
            new_name,
            additional_attrs=new_recipe.model_dump(),
        )

        new_recipe = self.repos.recipes.create(new_recipe)

        # Copy all assets (including images) to the new recipe directory
        # This assures that replaced links in recipe steps continue to work when the old recipe is deleted
        try:
            new_service = RecipeDataService(new_recipe.id, group_id=old_recipe.group_id)
            old_service = RecipeDataService(old_recipe.id, group_id=old_recipe.group_id)
            copytree(
                old_service.dir_data,
                new_service.dir_data,
                dirs_exist_ok=True,
            )
        except Exception as e:
            self.logger.error(f"Failed to copy assets from {old_recipe.slug} to {new_recipe.slug}: {e}")

        return new_recipe

    def _pre_update_check(self, slug: str, new_data: Recipe) -> Recipe:
        """
        gets the recipe from the database and performs a check to see if the user can update the recipe.
        If the user can't update the recipe, an exception is raised.

        Checks:
            - That the recipe exists
            - That the user can update the recipe (recipe is not locked or the user is the owner)
            - _if_ the user is locking the recipe, that they can lock the recipe (user is the owner)

        Args:
            slug (str): recipe slug
            new_data (Recipe): the new recipe data

        Raises:
            exceptions.PermissionDenied (403)
        """

        recipe = self._get_recipe(slug)

        if recipe is None or recipe.settings is None:
            raise exceptions.NoEntryFound("Recipe not found.")

        if not self.can_update(recipe):
            raise exceptions.PermissionDenied("You do not have permission to edit this recipe.")

        setting_lock = new_data.settings is not None and recipe.settings.locked != new_data.settings.locked
        if setting_lock and not self.can_lock_unlock(recipe):
            raise exceptions.PermissionDenied("You do not have permission to lock/unlock this recipe.")

        return recipe

    def update_one(self, slug: str, update_data: Recipe) -> Recipe:
        recipe = self._pre_update_check(slug, update_data)

        new_data = self.repos.recipes.update(slug, update_data)
        self.check_assets(new_data, recipe.slug)
        return new_data

    def patch_one(self, slug: str, patch_data: Recipe) -> Recipe:
        recipe: Recipe | None = self._pre_update_check(slug, patch_data)
        recipe = self._get_recipe(slug)

        if recipe is None:
            raise exceptions.NoEntryFound("Recipe not found.")

        new_data = self.repos.recipes.by_group(self.group.id).patch(
            recipe.slug, patch_data.model_dump(exclude_unset=True)
        )

        self.check_assets(new_data, recipe.slug)
        return new_data

    def update_last_made(self, slug: str, timestamp: datetime) -> Recipe:
        # we bypass the pre update check since any user can update a recipe's last made date, even if it's locked
        recipe = self._get_recipe(slug)
        return self.repos.recipes.by_group(self.group.id).patch(recipe.slug, {"last_made": timestamp})

    def delete_one(self, slug) -> Recipe:
        recipe = self._get_recipe(slug)

        if not self.can_update(recipe):
            raise exceptions.PermissionDenied("You do not have permission to delete this recipe.")

        data = self.repos.recipes.delete(recipe.id, "id")
        self.delete_assets(data)
        return data

    # =================================================================
    # Recipe Template Methods

    def render_template(self, recipe: Recipe, temp_dir: Path, template: str) -> Path:
        t_service = TemplateService(temp_dir)
        return t_service.render(recipe, template)
