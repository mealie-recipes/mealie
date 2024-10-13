import asyncio
import csv
from pathlib import Path
from typing import Any

from slugify import slugify

from mealie.schema.recipe.recipe import Recipe
from mealie.services.migrations.utils.migration_alias import MigrationAlias
from mealie.services.scraper import cleaner

from ._migration_base import BaseMigrator
from .utils.migration_helpers import scrape_image, split_by_line_break, split_by_semicolon

nutrition_map = {
    "carbohydrate": "carbohydrateContent",
    "protein": "proteinContent",
    "fat": "fatContent",
    "saturatedfat": "saturatedFatContent",
    "transfat": "transFatContent",
    "sodium": "sodiumContent",
    "fiber": "fiberContent",
    "sugar": "sugarContent",
    "unsaturatedfat": "unsaturatedFatContent",
}


class MyRecipeBoxMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "myrecipebox"

        self.key_aliases = [
            MigrationAlias(key="name", alias="title", func=None),
            MigrationAlias(key="prepTime", alias="preparationTime", func=self.parse_time),
            MigrationAlias(key="performTime", alias="cookingTime", func=self.parse_time),
            MigrationAlias(key="totalTime", alias="totalTime", func=self.parse_time),
            MigrationAlias(key="recipeYield", alias="quantity", func=str),
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=None),
            MigrationAlias(key="recipeInstructions", alias="instructions", func=split_by_line_break),
            MigrationAlias(key="notes", alias="notes", func=split_by_line_break),
            MigrationAlias(key="nutrition", alias="nutrition", func=self.parse_nutrition),
            MigrationAlias(key="recipeCategory", alias="categories", func=split_by_semicolon),
            MigrationAlias(key="tags", alias="tags", func=split_by_semicolon),
            MigrationAlias(key="orgURL", alias="source", func=None),
        ]

    def parse_time(self, time: Any) -> str | None:
        """Converts a time value to a string with minutes"""
        try:
            if not time:
                return None
            if not (isinstance(time, int) or isinstance(time, float) or isinstance(time, str)):
                time = str(time)

            if isinstance(time, str):
                try:
                    time = int(time)
                except ValueError:
                    return time

            unit = self.translator.t("datetime.minute", count=time)
            return f"{time} {unit}"
        except Exception:
            return None

    def parse_nutrition(self, input_: Any) -> dict | None:
        if not input_ or not isinstance(input_, str):
            return None

        nutrition = {}

        vals = (x.strip() for x in input_.split("\n") if x)
        for val in vals:
            try:
                key, value = (x.strip() for x in val.split(":", maxsplit=1))

                if not (key and value):
                    continue

                key = nutrition_map.get(key.lower(), key)

            except ValueError:
                continue

            nutrition[key] = value

        return cleaner.clean_nutrition(nutrition) if nutrition else None

    def extract_rows(self, file: Path) -> list[dict]:
        """Extracts the rows from the CSV file and returns a list of dictionaries"""
        rows: list[dict] = []
        with open(file, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        return rows

    def pre_process_row(self, row: dict) -> dict:
        if not (video := row.get("video")):
            return row

        # if there is no source, use the video as the source
        if not row.get("source"):
            row["source"] = video
            return row

        # otherwise, add the video as a note
        notes = row.get("notes", "")
        if notes:
            notes = f"{notes}\n{video}"
        else:
            notes = video

        row["notes"] = notes
        return row

    def _migrate(self) -> None:
        recipe_image_urls: dict = {}

        recipes: list[Recipe] = []
        for row in self.extract_rows(self.archive):
            recipe_dict = self.pre_process_row(row)
            if (title := recipe_dict.get("title")) and (image_url := recipe_dict.get("originalPicture")):
                try:
                    slug = slugify(title)
                    recipe_image_urls[slug] = image_url
                except Exception:
                    pass

            recipe_model = self.clean_recipe_dictionary(recipe_dict)
            recipes.append(recipe_model)

        results = self.import_recipes_to_database(recipes)
        for slug, recipe_id, status in results:
            if not status or not (recipe_image_url := recipe_image_urls.get(slug)):
                continue

            try:
                asyncio.run(scrape_image(recipe_image_url, recipe_id))
            except Exception as e:
                self.logger.error(f"Failed to download image for {slug}: {e}")
