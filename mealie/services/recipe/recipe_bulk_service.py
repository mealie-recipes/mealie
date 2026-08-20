from pathlib import Path

from pydantic import UUID4

from mealie.core.exceptions import NoEntryFound, PermissionDenied, UnexpectedNone
from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.recipe import CategoryBase
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_bulk_actions import BulkOrganizeRecipes
from mealie.schema.recipe.recipe_category import TagBase
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user.user import GroupInDB, PrivateUser
from mealie.services._base_service import BaseService
from mealie.services.exporter import Exporter, RecipeExporter
from mealie.services.recipe.recipe_service import RecipeService


class RecipeBulkActionsService(BaseService):
    def __init__(
        self,
        repos: AllRepositories,
        user: PrivateUser,
        group: GroupInDB,
        household: HouseholdInDB | None = None,
        translator: Translator | None = None,
    ):
        self.repos = repos
        self.user = user
        self.group = group
        self.recipe_service = RecipeService(repos, user, household, translator) if household and translator else None
        super().__init__()

    def organize_recipes(self, data: BulkOrganizeRecipes) -> list[Recipe]:
        recipe_service = self.recipe_service
        if recipe_service is None:
            raise RuntimeError("Recipe service dependencies are required for organizer updates")

        group_recipes = recipe_service.group_recipes
        requested_ids = set(data.recipes)
        loaded_recipes = group_recipes.get_models_by_ids(data.recipes)
        loaded_by_id = {recipe.id: recipe for recipe in loaded_recipes}

        if set(loaded_by_id) != requested_ids:
            raise NoEntryFound("One or more recipes were not found.")

        recipes = [loaded_by_id[recipe_id] for recipe_id in data.recipes]
        recipe_slugs = [recipe.slug for recipe in recipes]
        if not recipe_service.can_update(recipe_slugs):
            raise PermissionDenied("You do not have permission to edit all of these recipes.")

        tag_ids = [tag.id for tag in data.tags]
        category_ids = [category.id for category in data.categories]
        tags = self.repos.tags.get_models_by_ids(tag_ids)
        categories = self.repos.categories.get_models_by_ids(category_ids)

        if {tag.id for tag in tags} != set(tag_ids):
            raise NoEntryFound("One or more tags were not found.")
        if {category.id for category in categories} != set(category_ids):
            raise NoEntryFound("One or more categories were not found.")

        return group_recipes.bulk_update_organizers(recipes, tags, categories, data.operation)

    def export_recipes(self, temp_path: Path, slugs: list[str]) -> None:
        recipe_exporter = RecipeExporter(self.repos, self.group.id, slugs)
        exporter = Exporter(self.group.id, temp_path, [recipe_exporter])

        exporter.run(self.repos)

    def get_exports(self) -> list[GroupDataExport]:
        exports_page = self.repos.group_exports.page_all(PaginationQuery(per_page=-1))
        return exports_page.items

    def get_export(self, id: UUID4) -> GroupDataExport | None:
        return self.repos.group_exports.get_one(id)

    def purge_exports(self) -> int:
        all_exports = self.get_exports()

        exports_deleted = 0
        for export in all_exports:
            try:
                Path(export.path).unlink(missing_ok=True)
                self.repos.group_exports.delete(export.id)
                exports_deleted += 1
            except Exception as e:
                self.logger.error(f"Failed to delete export {export.id}")
                self.logger.error(e)

        group = self.repos.groups.get_one(self.group.id)

        if group is None:
            raise UnexpectedNone("Failed to purge exports for group, no group found")

        for match in group.directory.glob("**/export/*zip"):
            if match.is_file():
                match.unlink()
                exports_deleted += 1

        return exports_deleted

    def set_settings(self, recipes: list[str], settings: RecipeSettings) -> None:
        for slug in recipes:
            recipe = self.repos.recipes.get_one(slug)

            if recipe is None or recipe.settings is None:
                raise UnexpectedNone(f"Failed to set settings for recipe {slug}, no recipe found")

            settings.locked = recipe.settings.locked
            recipe.settings = settings

            try:
                self.repos.recipes.update(slug, recipe)
            except Exception as e:
                self.logger.error(f"Failed to set settings for recipe {slug}")
                self.logger.error(e)

    def assign_tags(self, recipes: list[str], tags: list[TagBase]) -> None:
        for slug in recipes:
            recipe = self.repos.recipes.get_one(slug)

            if recipe is None:
                raise UnexpectedNone(f"Failed to tag recipe {slug}, no recipe found")

            if recipe.tags is None:
                recipe.tags = []

            recipe.tags += tags  # type: ignore

            try:
                self.repos.recipes.update(slug, recipe)
            except Exception as e:
                self.logger.error(f"Failed to tag recipe {slug}")
                self.logger.error(e)

    def assign_categories(self, recipes: list[str], categories: list[CategoryBase]) -> None:
        for slug in recipes:
            recipe = self.repos.recipes.get_one(slug)

            if recipe is None:
                raise UnexpectedNone(f"Failed to categorize recipe {slug}, no recipe found")

            if recipe.recipe_category is None:
                recipe.recipe_category = []

            recipe.recipe_category += categories  # type: ignore

            try:
                self.repos.recipes.update(slug, recipe)
            except Exception as e:
                self.logger.error(f"Failed to categorize recipe {slug}")
                self.logger.error(e)
