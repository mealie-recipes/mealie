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
                yield from reader


def get_value_as_string_or_none(dictionary: dict, key: str):
    value = dictionary.get(key)
    if value is not None:
        try:
            return str(value)
        except Exception:
            return None
    else:
        return None


nutrition_map = {
    "Calories": "calories",
    "Fat": "fatContent",
    "Saturated Fat": "saturatedFatContent",
    "Cholesterol": "cholesterolContent",
    "Sodium": "sodiumContent",
    "Sugar": "sugarContent",
    "Carbohydrate": "carbohydrateContent",
    "Fiber": "fiberContent",
    "Protein": "proteinContent",
}


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
            MigrationAlias(key="dateAdded", alias="Created At", func=lambda x: x[: x.find(" ")]),
        ]

    def _parse_recipe_nutrition_from_row(self, row: dict) -> dict:
        """Parses the nutrition data from the row"""
        nut_dict = {normalized_k: row[k] for k, normalized_k in nutrition_map.items() if k in row}

        return cleaner.clean_nutrition(nut_dict)

    def _get_categories_from_row(self, row: dict) -> list[str]:
        """Parses various category-like columns into categories"""

        categories: list[str] = []
        columns = ["Course", "Cuisine"]
        for column in columns:
            value = get_value_as_string_or_none(row, column)
            if value:
                categories.append(value)

        return categories

    def _get_tags_from_row(self, row: dict) -> list[str]:
        tag_str = get_value_as_string_or_none(row, "Tags")
        tags = split_by_comma(tag_str) or []
        main_ingredient = get_value_as_string_or_none(row, "Main Ingredient")
        if main_ingredient:
            tags.append(main_ingredient)

        return tags

    def _process_recipe_row(self, row: dict) -> dict:
        """Reads a single recipe's row, merges columns, and converts the row to a dictionary"""

        recipe_dict: dict = row

        recipe_dict["recipeCategory"] = self._get_categories_from_row(row)
        recipe_dict["tags"] = self._get_tags_from_row(row)
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
