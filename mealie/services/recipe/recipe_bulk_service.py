from pathlib import Path

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.recipe import CategoryBase
from mealie.schema.recipe.recipe_category import TagBase
from mealie.schema.user.user import GroupInDB, PrivateUser
from mealie.services._base_service import BaseService
from mealie.services.exporter import Exporter, RecipeExporter


class RecipeBulkActionsService(BaseService):
    def __init__(self, repos: AllRepositories, user: PrivateUser, group: GroupInDB):
        self.repos = repos
        self.user = user
        self.group = group
        super().__init__()

    def export_recipes(self, temp_path: Path, slugs: list[str]) -> None:
        recipe_exporter = RecipeExporter(self.repos, self.group.id, slugs)
        exporter = Exporter(self.group.id, temp_path, [recipe_exporter])

        exporter.run(self.repos)

    def get_exports(self) -> list[GroupDataExport]:
        return self.repos.group_exports.multi_query({"group_id": self.group.id})

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

        for match in group.directory.glob("**/export/*zip"):
            if match.is_file():
                match.unlink()
                exports_deleted += 1

        return exports_deleted

    def assign_tags(self, recipes: list[str], tags: list[TagBase]) -> None:
        for slug in recipes:
            recipe = self.repos.recipes.get_one(slug)

            if recipe is None:
                self.logger.error(f"Failed to tag recipe {slug}, no recipe found")

            recipe.tags += tags

            try:
                self.repos.recipes.update(slug, recipe)
            except Exception as e:
                self.logger.error(f"Failed to tag recipe {slug}")
                self.logger.error(e)

    def assign_categories(self, recipes: list[str], categories: list[CategoryBase]) -> None:
        for slug in recipes:
            recipe = self.repos.recipes.get_one(slug)

            if recipe is None:
                self.logger.error(f"Failed to categorize recipe {slug}, no recipe found")

            recipe.recipe_category += categories

            try:
                self.repos.recipes.update(slug, recipe)
            except Exception as e:
                self.logger.error(f"Failed to categorize recipe {slug}")
                self.logger.error(e)

    def delete_recipes(self, recipes: list[str]) -> None:
        for slug in recipes:
            try:
                self.repos.recipes.delete(slug)
            except Exception as e:
                self.logger.error(f"Failed to delete recipe {slug}")
                self.logger.error(e)
