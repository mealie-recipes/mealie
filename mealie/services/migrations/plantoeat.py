import asyncio
import csv
import tempfile
import zipfile
from pathlib import Path

from slugify import slugify

from mealie.pkgs.cache import cache_key
from mealie.services.scraper import cleaner

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import scrape_image, split_by_comma


def plantoeat_recipes(file: Path):
    """Yields all recipes inside the export file as dict"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(file) as zip_file:
            zip_file.extractall(tmpdir)

        for name in Path(tmpdir).glob("**/[!.]*.csv"):
            with open(name, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    yield row


def get_value_as_string_or_none(dictionary: dict, key: str):
    value = dictionary.get(key)
    if value is not None:
        try:
            return str(value)
        except Exception:
            return None
    else:
        return None


class PlanToEatMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "plantoeat"

        self.key_aliases = [
            MigrationAlias(key="name", alias="Title"),
            MigrationAlias(key="description", alias="Description"),
            MigrationAlias(
                key="recipeIngredient",
                alias="Ingredients",
                func=lambda x: [z for z in x.splitlines() if z.strip() and not z.startswith(", ")],
            ),
            MigrationAlias(key="recipeInstructions", alias="Directions"),
            MigrationAlias(key="recipeYield", alias="Servings"),
            MigrationAlias(key="orgURL", alias="Url"),
            MigrationAlias(key="rating", alias="Rating"),
            MigrationAlias(key="prepTime", alias="Prep Time"),
            MigrationAlias(key="performTime", alias="Cook Time"),
            MigrationAlias(key="totalTime", alias="Total Time"),
            MigrationAlias(key="tags", alias="Tags", func=split_by_comma),
            MigrationAlias(key="dateAdded", alias="Created At", func=lambda x: x[: x.find(" ")]),
        ]

    def _parse_recipe_nutrition_from_row(self, row: dict) -> dict:
        """Parses the nutrition data from the row"""

        nut_dict: dict = {}

        nut_dict["calories"] = get_value_as_string_or_none(row, "Calories")
        nut_dict["fatContent"] = get_value_as_string_or_none(row, "Fat")
        nut_dict["proteinContent"] = get_value_as_string_or_none(row, "Protein")
        nut_dict["carbohydrateContent"] = get_value_as_string_or_none(row, "Carbohydrate")
        nut_dict["fiberContent"] = get_value_as_string_or_none(row, "Fiber")
        nut_dict["sodiumContent"] = get_value_as_string_or_none(row, "Sodium")
        nut_dict["sugarContent"] = get_value_as_string_or_none(row, "Sugar")

        return cleaner.clean_nutrition(nut_dict)

    def _process_recipe_row(self, row: dict) -> dict:
        """Reads a single recipe's row, parses its nutrition, and converts it to a dictionary"""

        recipe_dict: dict = row

        recipe_dict["nutrition"] = self._parse_recipe_nutrition_from_row(row)

        return recipe_dict

    def _migrate(self) -> None:
        recipe_image_urls = {}

        recipes = []
        for recipe in plantoeat_recipes(self.archive):
            if "Title" not in recipe:
                continue

            if "Photo Url" in recipe:
                recipe_image_urls[slugify(recipe["Title"])] = recipe["Photo Url"]
                recipe["image"] = cache_key.new_key(4)

            preprocess_recipe = self._process_recipe_row(recipe)

            recipe_model = self.clean_recipe_dictionary(preprocess_recipe)

            recipes.append(recipe_model)

        results = self.import_recipes_to_database(recipes)

        for slug, recipe_id, status in results:
            if not status:
                continue

            try:
                asyncio.run(scrape_image(recipe_image_urls[slug], recipe_id))
            except Exception as e:
                self.logger.error(f"Failed to download image for {slug}: {e}")
