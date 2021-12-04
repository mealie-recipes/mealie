from __future__ import annotations

from pathlib import Path

from mealie.core.root_logger import get_logger
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.recipe import CategoryBase, Recipe
from mealie.schema.recipe.recipe_category import TagBase
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event
from mealie.services.exporter import Exporter, RecipeExporter

logger = get_logger(__name__)


class RecipeBulkActions(UserHttpService[int, Recipe]):
    event_func = create_recipe_event
    _restrict_by_group = True

    def populate_item(self, _: int) -> Recipe:
        return

    def export_recipes(self, temp_path: Path, slugs: list[str]) -> None:
        recipe_exporter = RecipeExporter(self.db, self.group_id, slugs)
        exporter = Exporter(self.group_id, temp_path, [recipe_exporter])

        exporter.run(self.db)

    def get_exports(self) -> list[GroupDataExport]:
        return self.db.group_exports.multi_query({"group_id": self.group_id})

    def purge_exports(self) -> int:
        all_exports = self.get_exports()

        exports_deleted = 0
        for export in all_exports:
            try:
                Path(export.path).unlink(missing_ok=True)
                self.db.group_exports.delete(export.id)
                exports_deleted += 1
            except Exception as e:
                logger.error(f"Failed to delete export {export.id}")
                logger.error(e)

        group = self.db.groups.get_one(self.group_id)

        for match in group.directory.glob("**/export/*zip"):
            if match.is_file():
                match.unlink()
                exports_deleted += 1

        return exports_deleted

    def assign_tags(self, recipes: list[str], tags: list[TagBase]) -> None:
        for slug in recipes:
            recipe = self.db.recipes.get_one(slug)

            if recipe is None:
                logger.error(f"Failed to tag recipe {slug}, no recipe found")

            recipe.tags += tags

            try:
                self.db.recipes.update(slug, recipe)
            except Exception as e:
                logger.error(f"Failed to tag recipe {slug}")
                logger.error(e)

    def assign_categories(self, recipes: list[str], categories: list[CategoryBase]) -> None:
        for slug in recipes:
            recipe = self.db.recipes.get_one(slug)

            if recipe is None:
                logger.error(f"Failed to categorize recipe {slug}, no recipe found")

            recipe.recipe_category += categories

            try:
                self.db.recipes.update(slug, recipe)
            except Exception as e:
                logger.error(f"Failed to categorize recipe {slug}")
                logger.error(e)

    def delete_recipes(self, recipes: list[str]) -> None:
        for slug in recipes:
            try:
                self.db.recipes.delete(slug)
            except Exception as e:
                logger.error(f"Failed to delete recipe {slug}")
                logger.error(e)
