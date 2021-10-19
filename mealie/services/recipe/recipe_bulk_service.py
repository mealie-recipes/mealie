from __future__ import annotations

from pathlib import Path

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import CategoryBase, Recipe
from mealie.schema.recipe.recipe_category import TagBase
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event

logger = get_logger(__name__)


class RecipeBulkActions(UserHttpService[int, Recipe]):
    event_func = create_recipe_event
    _restrict_by_group = True

    def populate_item(self, _: int) -> Recipe:
        return

    def export_recipes(self, temp_path: Path, recipes: list[str]) -> None:
        return

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
