from typing import Iterator
from uuid import UUID

from mealie.repos.all_repositories import AllRepositories
from mealie.schema.recipe import Recipe

from ._abc_exporter import ABCExporter, ExportedItem


class RecipeExporter(ABCExporter):
    def __init__(self, db: AllRepositories, group_id: UUID, recipes: list[str]) -> None:
        """
        RecipeExporter is used to export a list of recipes to a zip file. The zip
        file is then saved to a temporary directory and then available for a one-time
        download.

        Args:
            db (Database):
            group_id (int):
            recipes (list[str]): Recipe Slugs
        """
        super().__init__(db, group_id)
        self.recipes = recipes

    @property
    def destination_dir(self) -> str:
        return "recipes"

    def items(self) -> Iterator[ExportedItem]:
        for slug in self.recipes:
            yield ExportedItem(
                name=slug,
                model=self.db.recipes.multi_query({"slug": slug, "group_id": self.group_id}, limit=1)[0],
            )

    def _post_export_hook(self, item: Recipe) -> None:
        """Copy recipe directory contents into the zip folder"""
        recipe_dir = item.directory

        if recipe_dir.exists():
            self.write_dir_to_zip(recipe_dir, f"{self.destination_dir}/{item.slug}", {".json"})
