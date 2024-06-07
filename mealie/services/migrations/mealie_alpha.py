import contextlib
import shutil
import tempfile
import zipfile
from pathlib import Path

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.reports.reports import ReportEntryCreate

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, split_by_comma


class MealieAlphaMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "mealie_alpha"

        self.key_aliases = [
            MigrationAlias(key="name", alias="title", func=None),
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=None),
            MigrationAlias(key="recipeInstructions", alias="directions", func=None),
            MigrationAlias(key="tags", alias="tags", func=split_by_comma),
        ]

    @classmethod
    def get_zip_base_path(cls, path: Path) -> Path:
        potential_path = super().get_zip_base_path(path)
        if path == potential_path:
            return path

        # make sure we didn't accidentally open the "recipes" dir
        if potential_path.name == "recipes":
            return path
        else:
            return potential_path

    def _convert_to_new_schema(self, recipe: dict) -> Recipe:
        if recipe.get("categories", False):
            recipe["recipeCategory"] = recipe.get("categories")
            del recipe["categories"]

        with contextlib.suppress(KeyError):
            del recipe["_id"]
            del recipe["date_added"]
        # Migration from list to Object Type Data
        with contextlib.suppress(KeyError):
            if "" in recipe["tags"]:
                recipe["tags"] = [tag for tag in recipe["tags"] if tag != ""]
        with contextlib.suppress(KeyError):
            if "" in recipe["categories"]:
                recipe["categories"] = [cat for cat in recipe["categories"] if cat != ""]
        if isinstance(recipe["extras"], list):
            recipe["extras"] = {}

        recipe["comments"] = []

        # Reset ID on migration
        recipe["id"] = None

        return Recipe(**recipe)

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            temp_path = self.get_zip_base_path(Path(tmpdir))
            recipe_lookup: dict[str, Path] = {}

            recipes: list[Recipe] = []
            for recipe_json_path in temp_path.rglob("**/recipes/**/[!.]*.json"):
                try:
                    if (recipe_as_dict := MigrationReaders.json(recipe_json_path)) is not None:
                        recipe = self._convert_to_new_schema(recipe_as_dict)
                        recipes.append(recipe)
                        slug = recipe_as_dict["slug"]
                        recipe_lookup[slug] = recipe_json_path.parent
                except Exception as e:
                    self.logger.exception(e)
                    self.report_entries.append(
                        ReportEntryCreate(
                            report_id=self.report_id,
                            success=False,
                            message=f"Failed to import {recipe_json_path.name}",
                            exception=f"{e.__class__.__name__}: {e}",
                        )
                    )

            results = self.import_recipes_to_database(recipes)
            for slug, recipe_id, status in results:
                if not status:
                    continue

                dest_dir = Recipe.directory_from_id(recipe_id)
                source_dir = recipe_lookup.get(slug)

                if dest_dir.exists():
                    shutil.rmtree(dest_dir)

                if source_dir is None:
                    continue

                for dir in source_dir.iterdir():
                    if dir.is_dir():
                        shutil.copytree(dir, dest_dir / dir.name)
