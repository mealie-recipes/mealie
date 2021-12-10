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

        return Recipe(**recipe)

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            temp_path = Path(tmpdir)

            recipe_lookup: dict[str, Path] = {}
            recipes_as_dicts = []

            for x in temp_path.rglob("**/[!.]*.json"):
                if (y := MigrationReaders.json(x)) is not None:
                    recipes_as_dicts.append(y)
                    slug = y["slug"]
                    recipe_lookup[slug] = x.parent

            recipes = [self._convert_to_new_schema(x) for x in recipes_as_dicts]

            results = self.import_recipes_to_database(recipes)

            recipe_model_lookup = {x.slug: x for x in recipes}

            for slug, status in results:
                if status:
                    model = recipe_model_lookup.get(slug)
                    dest_dir = model.directory
                    source_dir = recipe_lookup.get(slug)

                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)

                    shutil.copytree(source_dir, dest_dir)
