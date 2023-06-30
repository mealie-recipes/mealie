import json
import os
import tempfile
import zipfile
from datetime import timedelta
from fractions import Fraction
from pathlib import Path
from typing import Any

from mealie.schema.group.group_shopping_list import display_fraction
from mealie.schema.recipe.recipe_ingredient import INGREDIENT_QTY_PRECISION, MAX_INGREDIENT_DENOMINATOR
from mealie.schema.reports.reports import ReportEntryCreate

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import import_image


def _build_ingredient_from_ingredient_data(ingredient_data: dict[str, Any], title: str | None = None) -> dict[str, Any]:
    ingredient_parts: list[str] = []

    # TODO: quantity formatting is copied from the shopping list item schema, and probably shouldn't be
    amount = round(float(ingredient_data.get("amount", "1")), INGREDIENT_QTY_PRECISION)
    quantity = Fraction(amount).limit_denominator(MAX_INGREDIENT_DENOMINATOR)
    if quantity.denominator == 1:
        ingredient_parts.append(str(quantity))
    elif quantity.numerator <= quantity.denominator:
        ingredient_parts.append(display_fraction(quantity))
    else:
        # convert an improper fraction into a mixed fraction (e.g. 11/4 --> 2 3/4)
        whole_number = 0
        while quantity.numerator > quantity.denominator:
            whole_number += 1
            quantity -= 1

        ingredient_parts.append(f"{whole_number} {display_fraction(quantity)}")

    if unit := ingredient_data.get("unit"):
        if unit_name := unit.get("name"):
            ingredient_parts.append(unit_name)
        elif unit_plural_name := unit.get("plural_name"):
            ingredient_parts.append(unit_plural_name)

    if food := ingredient_data.get("food"):
        if food_name := food.get("name"):
            ingredient_parts.append(food_name)
        elif food_plural_name := food.get("plural_name"):
            ingredient_parts.append(food_plural_name)

    if note := ingredient_data.get("note"):
        ingredient_parts.append(note)

    text = " ".join(ingredient_parts)
    return {"title": title, "note": text}


def extract_instructions_and_ingredients(steps: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    """Returns a list of instructions and ingredients for a recipe"""

    instructions: list[str] = []
    ingredients: list[dict[str, Any]] = []
    for step in steps:
        if instruction_text := step.get("instruction"):
            instructions.append(instruction_text)
        if ingredients_data := step.get("ingredients"):
            for i, ingredient in enumerate(ingredients_data):
                if not i and (title := step.get("name")):
                    ingredients.append(_build_ingredient_from_ingredient_data(ingredient, title))
                else:
                    ingredients.append(_build_ingredient_from_ingredient_data(ingredient))

    return instructions, ingredients


def _format_time(minutes: int) -> str:
    # TODO: make this translatable
    hour_label = "hour"
    hours_label = "hours"
    minute_label = "minute"
    minutes_label = "minutes"

    hours, minutes = divmod(minutes, 60)
    parts: list[str] = []

    if hours:
        parts.append(f"{int(hours)} {hour_label if hours == 1 else hours_label}")
    if minutes:
        parts.append(f"{minutes} {minute_label if minutes == 1 else minutes_label}")

    return " ".join(parts)


def parse_times(working_time: int, waiting_time: int) -> tuple[str, str]:
    """Returns the performTime and totalTime"""

    total_time = working_time + waiting_time
    return _format_time(working_time), _format_time(total_time)


class TandoorMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "tandoor"

        self.key_aliases = [
            MigrationAlias(key="tags", alias="keywords", func=lambda kws: [kw["name"] for kw in kws if kw.get("name")]),
            MigrationAlias(key="orgURL", alias="source_url", func=None),
        ]

    def _process_recipe_document(self, source_dir: Path, recipe_data: dict) -> dict:
        steps_data = recipe_data.pop("steps", [])
        recipe_data["recipeInstructions"], recipe_data["recipeIngredient"] = extract_instructions_and_ingredients(
            steps_data
        )
        recipe_data["performTime"], recipe_data["totalTime"] = parse_times(
            recipe_data.pop("working_time", 0), recipe_data.pop("waiting_time", 0)
        )

        serving_size = recipe_data.pop("servings", 0)
        serving_text = recipe_data.pop("servings_text", "")
        if serving_size and serving_text:
            recipe_data["recipeYield"] = f"{serving_size} {serving_text}"

        recipe_data["image"] = str(source_dir.joinpath("image.jpeg"))
        return recipe_data

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            source_dir = Path(tmpdir)

            recipes_as_dicts: list[dict] = []
            for i, recipe_zip_file in enumerate(source_dir.glob("*.zip")):
                try:
                    recipe_dir = str(source_dir.joinpath(f"recipe_{i+1}"))
                    os.makedirs(recipe_dir)

                    with zipfile.ZipFile(recipe_zip_file) as recipe_zip:
                        recipe_zip.extractall(recipe_dir)

                    recipe_source_dir = Path(recipe_dir)
                    recipe_json_path = recipe_source_dir.joinpath("recipe.json")
                    with open(recipe_json_path) as f:
                        recipes_as_dicts.append(self._process_recipe_document(recipe_source_dir, json.load(f)))

                except Exception as e:
                    self.report_entries.append(
                        ReportEntryCreate(
                            report_id=self.report_id,
                            success=False,
                            message="Failed to parse recipe",
                            exception=f"{type(e).__name__}: {e}",
                        )
                    )

            recipes = [self.clean_recipe_dictionary(x) for x in recipes_as_dicts]
            results = self.import_recipes_to_database(recipes)
            recipe_lookup = {r.slug: r for r in recipes}
            for slug, recipe_id, status in results:
                if status:
                    try:
                        r = recipe_lookup.get(slug)
                        if not r or not r.image:
                            continue

                    except StopIteration:
                        continue

                    import_image(r.image, recipe_id)
