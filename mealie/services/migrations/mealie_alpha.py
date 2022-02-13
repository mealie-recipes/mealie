import shutil
import tempfile
import zipfile
from pathlib import Path

from mealie.schema.recipe.recipe import Recipe

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

    def _convert_to_new_schema(self, recipe: dict) -> Recipe:
        if recipe.get("categories", False):
            recipe["recipeCategory"] = recipe.get("categories")
            del recipe["categories"]
        try:
            del recipe["_id"]
            del recipe["date_added"]
        except Exception:
            pass

        # Migration from list to Object Type Data
        try:
            if "" in recipe["tags"]:
                recipe["tags"] = [tag for tag in recipe["tags"] if tag != ""]
        except Exception:
            pass

        try:
            if "" in recipe["categories"]:
                recipe["categories"] = [cat for cat in recipe["categories"] if cat != ""]
        except Exception:
            pass

        if type(recipe["extras"]) == list:
            recipe["extras"] = {}

        recipe["comments"] = []

        # Reset ID on migration
        recipe["id"] = None

        return Recipe(**recipe)

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            temp_path = Path(tmpdir)

            recipe_lookup: dict[str, Path] = {}
            recipes_as_dicts = []

            for x in temp_path.rglob("**/recipes/**/[!.]*.json"):
                if (y := MigrationReaders.json(x)) is not None:
                    recipes_as_dicts.append(y)
                    slug = y["slug"]
                    recipe_lookup[slug] = x.parent

            recipes = [self._convert_to_new_schema(x) for x in recipes_as_dicts]

            results = self.import_recipes_to_database(recipes)

            for slug, recipe_id, status in results:
                if not status:
                    continue

                dest_dir = Recipe.directory_from_id(recipe_id)
                source_dir = recipe_lookup.get(slug)

                if dest_dir.exists():
                    shutil.rmtree(dest_dir)

                for dir in source_dir.iterdir():
                    if dir.is_dir():
                        shutil.copytree(dir, dest_dir / dir.name)
