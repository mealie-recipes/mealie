import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientFood, SaveIngredientUnit
from mealie.schema.reports.reports import ReportEntryCreate
from mealie.services.parser_services._base import DataMatcher
from mealie.services.parser_services.parser_utils.string_utils import extract_quantity_from_string

from ._migration_base import BaseMigrator
from .utils.migration_helpers import format_time


class DSVParser:
    def __init__(self, directory: Path):
        self.directory = directory
        self.tables: dict[str, list[dict[str, Any]]] = {}
        self.load_files()

    def load_files(self) -> None:
        """Loads all .dsv files from the directory into lists of dictionaries."""
        for file in self.directory.glob("*.dsv"):
            with open(file, "rb") as f:
                file_contents = f.read().decode("utf-8", errors="ignore")

            # Replace unique delimiters
            file_contents = file_contents.replace("||||", "\x06")
            file_contents = file_contents.replace("!@#%^&*()", "\x07")

            # Manually parse rows
            rows = file_contents.strip().split("\x07")
            if not rows:
                continue  # Skip empty files

            # Extract header
            headers = rows[0].split("\x06")
            data = [dict(zip(headers, row.split("\x06"), strict=False)) for row in rows[1:] if row]

            self.tables[file.stem] = data  # Store parsed table

    def query_by_id(self, table_name: str, column_name: str, ids: list[str]) -> list[dict[str, Any]]:
        """Returns rows from a specified table where column_name matches any of the provided IDs."""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found.")

        results = [row for row in self.tables[table_name] if row.get(column_name) in ids]

        if len(results) == 0:
            results.append({})

        return results

    def get_data(self, row: dict[str, Any], column: str) -> Any:
        """Get column data from row. Handles a few bad data cases."""
        data = row.get(column, "")
        if data is None or data == "[null]":
            data = ""
        return data

    def get_table(self, table_name: str) -> list[dict[str, Any]]:
        """Returns the entire table as a list of dictionaries."""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found.")
        return self.tables[table_name]

    def list_tables(self) -> list[str]:
        """Returns a list of available tables."""
        return list(self.tables.keys())


class CooknMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "cookn"
        self.key_aliases = []
        self.matcher = DataMatcher(self.db, food_fuzzy_match_threshold=95, unit_fuzzy_match_threshold=100)

    def _parse_units_table(self, db: DSVParser):
        """Parses the Cook'n units table and adds missing units to Mealie DB."""
        _units_table = db.get_table("temp_unit")
        for _unit_row in _units_table:
            name = db.get_data(_unit_row, "NAME")
            plural_name = db.get_data(_unit_row, "PLURAL_NAME")
            abbreviation = db.get_data(_unit_row, "ABBREVIATION")

            # exact match
            if not name or name in self.matcher.units_by_alias:
                continue

            # fuzzy match
            match = self.matcher.find_unit_match(name)
            if match is None:
                save = SaveIngredientUnit(
                    group_id=self.group.id,
                    name=name,
                    plural_name=plural_name,
                    abbreviation=abbreviation,
                )
                # update DataMatcher
                self.matcher = DataMatcher(self.db, food_fuzzy_match_threshold=95, unit_fuzzy_match_threshold=100)
                try:
                    self.db.ingredient_units.create(save)
                except Exception as e:
                    self.logger.error(e)
            else:
                self.logger.debug("Fuzzy match for unit (%s -> %s)", name, match.name)

    def _parse_foods_table(self, db: DSVParser):
        """Parses the Cook'n food table and adds missing foods to Mealie DB."""
        _foods_table = db.get_table("temp_food")
        for _food_row in _foods_table:
            name = db.get_data(_food_row, "NAME")
            plural_name = db.get_data(_food_row, "PLURAL_NAME")

            # exact match
            if not name or name in self.matcher.foods_by_alias:
                continue

            match = self.matcher.find_food_match(name)
            if match is None:
                save = SaveIngredientFood(group_id=self.group.id, name=name, plural_name=plural_name, description="")
                # update DataMatcher
                self.matcher = DataMatcher(self.db, food_fuzzy_match_threshold=95, unit_fuzzy_match_threshold=100)
                try:
                    self.db.ingredient_foods.create(save)
                except Exception as e:
                    self.logger.error(e)
            else:
                self.logger.debug("Fuzzy match for food (%s -> %s)", name, match.name)

    def _parse_media(self, _cookbook_id: str, _chapter_id: str, _recipe_id: str, db: DSVParser) -> str | None:
        """Checks recipe, chapter, and cookbook for images. Return path to most specific available image."""
        _media_recipe_row = db.query_by_id("temp_media", "ENTITY_ID", [_recipe_id])[0]
        _media_chapter_row = db.query_by_id("temp_media", "ENTITY_ID", [_chapter_id])[0]
        _media_cookbook_row = db.query_by_id("temp_media", "ENTITY_ID", [_cookbook_id])[0]

        # Get recipe image
        _media_row = _media_recipe_row
        _media_id = db.get_data(_media_row, "ID")
        if _media_id == "":
            # Get chapter image if no recipe image
            _media_row = _media_chapter_row
            _media_id = db.get_data(_media_row, "ID")
        if _media_id == "":
            # Get cookbook image if no chapter image
            _media_row = _media_cookbook_row
            _media_id = db.get_data(_media_row, "ID")

        # If we found an image
        if _media_id != "":
            _media_type = db.get_data(_media_row, "MEDIA_CONTENT_TYPE")
            # If the file has no extention add one (this is the normal case)
            if Path(str(_media_id)).suffix == "":
                if _media_type != "":
                    # Determine file extension based on media type
                    _extension = _media_type.split("/")[-1]
                    _old_image_path = os.path.join(db.directory, str(_media_id))
                    new_image_path = f"{_old_image_path}.{_extension}"
                    # Rename the file if it exists and has no extension
                    if os.path.exists(_old_image_path) and not os.path.exists(new_image_path):
                        os.rename(_old_image_path, new_image_path)
                    if Path(new_image_path).exists():
                        return new_image_path
            else:
                return os.path.join(db.directory, str(_media_id))
        return None

    def _parse_ingredients(self, _recipe_id: str, db: DSVParser) -> list[RecipeIngredient]:
        """Parses ingredients for recipe from Cook'n ingredients table."""
        ingredients = []
        ingredients_order = []
        _ingredient_rows = db.query_by_id("temp_ingredient", "PARENT_ID", [_recipe_id])
        for _ingredient_row in _ingredient_rows:
            _unit_id = db.get_data(_ingredient_row, "AMOUNT_UNIT")
            _unit_row = db.query_by_id("temp_unit", "ID", [_unit_id])[0]
            _food_id = db.get_data(_ingredient_row, "INGREDIENT_FOOD_ID")
            _food_row = db.query_by_id("temp_food", "ID", [_food_id])[0]
            _brand_id = db.get_data(_ingredient_row, "BRAND_ID")
            _brand_row = db.query_by_id("temp_brand", "ID", [_brand_id])[0]

            amount_str = db.get_data(_ingredient_row, "AMOUNT_QTY_STRING")
            amount, _ = extract_quantity_from_string(amount_str)
            unit_name = db.get_data(_unit_row, "NAME")
            food_name = db.get_data(_food_row, "NAME")

            # Match unit and food from Mealie DB
            unit = self.matcher.find_unit_match(unit_name)
            food = self.matcher.find_food_match(food_name)

            pre_qualifier = db.get_data(_ingredient_row, "PRE_QUALIFIER").lstrip().rstrip()
            post_qualifier = db.get_data(_ingredient_row, "POST_QUALIFIER").lstrip().rstrip()
            brand = db.get_data(_brand_row, "NAME")

            # Combine pre-qualifier and post-qualifier into single note
            note = ""
            if pre_qualifier != "":
                if pre_qualifier[-1] == ",":
                    pre_qualifier = pre_qualifier[:-1]
                note += pre_qualifier
            if post_qualifier != "":
                if pre_qualifier != "":
                    note += ", "
                if post_qualifier[-1] == ",":
                    post_qualifier = post_qualifier[:-1]
                if post_qualifier[0] == ",":
                    post_qualifier = post_qualifier[1:].lstrip()
                note += post_qualifier

            # Remove empty lines (unless amount was a text input)
            if not amount and not unit and not food and not note:
                self.logger.debug("%s, %s", amount_str, type(amount_str))
                if amount_str and amount_str != "0":
                    note = amount_str
                else:
                    continue

            og_text = ""
            if amount_str != "0":
                og_text += amount_str + " "
            if unit_name:
                og_text += unit_name + " "
            if pre_qualifier:
                og_text += pre_qualifier + " "
            if food_name:
                og_text += food_name + " "
            if post_qualifier:
                og_text += post_qualifier + " "
            if brand:
                og_text += brand

            base_ingredient = RecipeIngredient(
                quantity=amount,
                unit=unit,
                food=food,
                note=note,
                original_text=og_text.strip(),
                disable_amount=False,
            )
            try:
                _display_order = db.get_data(_ingredient_row, "DISPLAY_ORDER")
                ingredients_order.append(int(_display_order))
                ingredients.append(base_ingredient)
            except ValueError:
                self.logger.warning("Invalid ingredient order: %s, %s", _display_order, base_ingredient.original_text)
                continue
        return [obj for _, obj in sorted(zip(ingredients_order, ingredients, strict=False))]

    def _parse_instructions(self, instructions: str) -> list[str]:
        """
        Parses recipe instructions into a list of steps.
        Detects numbered lists, bulleted lists, and plain new-line-separated steps.
        """
        # Detects numbered lists (1., 1), 1-, etc.) and bulleted lists (-, *, •)
        numbered_pattern = re.compile(r"^(\d+)[.)-]\s*(.*)")
        bullet_pattern = re.compile(r"^[\-*•]\s*(.*)")

        lines = instructions.splitlines()
        steps = []
        current_step: list[str] = []

        for line in lines:
            line = line.strip()

            if not line:
                continue  # Skip empty lines

            num_match = numbered_pattern.match(line)
            bullet_match = bullet_pattern.match(line)

            if num_match:
                # If there's a current step, store it before starting a new one
                if current_step:
                    steps.append("\n".join(current_step))
                    current_step = []

                current_step.append(num_match.group(2))
            elif bullet_match:
                if current_step:
                    steps.append("\n".join(current_step))
                    current_step = []

                current_step.append(bullet_match.group(1))
            else:
                # Continuation of a previous step
                if current_step:
                    current_step.append(line)
                else:
                    # If no clear separator is found, treat each new line as a new step
                    steps.append(line)

        if current_step:
            steps.append(" ".join(current_step))

        return steps

    def _process_recipe_document(self, _recipe_row: dict[str, Any], db: DSVParser) -> dict:
        """Parses recipe row from the Cook'n recipe table."""
        recipe_data: dict[str, str | list[str] | list[RecipeIngredient]] = {}

        # Select db values
        _recipe_id = db.get_data(_recipe_row, "ID")
        _recipe_desc_row = db.query_by_id("temp_recipe_desc", "ID", [_recipe_id])[0]
        _chapter_id = db.get_data(_recipe_desc_row, "PARENT")
        _chapter_row = db.query_by_id("temp_chapter_desc", "ID", [_chapter_id])[0]
        _cookbook_id = db.get_data(_chapter_row, "PARENT")
        _cookbook_row = db.query_by_id("temp_cookBook_desc", "ID", [_cookbook_id])[0]

        # Parse general recipe info
        cookbook = db.get_data(_cookbook_row, "TITLE")
        chapter = db.get_data(_chapter_row, "TITLE")
        name = db.get_data(_recipe_desc_row, "TITLE")
        description = db.get_data(_recipe_desc_row, "DESCRIPTION")
        serves = db.get_data(_recipe_row, "SERVES")
        try:
            prep_time = int(db.get_data(_recipe_row, "PREPTIME"))
        except ValueError:
            prep_time = 0
        try:
            cook_time = int(db.get_data(_recipe_row, "COOKTIME"))
        except ValueError:
            cook_time = 0

        recipe_data["recipeCategory"] = [cookbook + " - " + chapter]
        recipe_data["name"] = name
        recipe_data["description"] = description
        recipe_data["recipeYield"] = serves
        recipe_data["prepTime"] = format_time(prep_time)
        recipe_data["performTime"] = format_time(cook_time)
        recipe_data["totalTime"] = format_time(prep_time + cook_time)

        # Parse image file
        image_path = self._parse_media(_cookbook_id, _chapter_id, _recipe_id, db)
        if image_path is not None:
            recipe_data["image"] = [image_path]

        # Parse ingredients
        recipe_data["_parsed_ingredients"] = self._parse_ingredients(_recipe_id, db)

        # Parse instructions
        recipe_data["recipeInstructions"] = self._parse_instructions(db.get_data(_recipe_row, "INSTRUCTIONS"))

        return recipe_data

    def _process_cookbook(self, path: Path) -> None:
        """Processes contents of a zip file."""
        source_dir = self.get_zip_base_path(path)
        db = DSVParser(source_dir)
        # Load units and foods from Cook'n
        self._parse_units_table(db)
        self._parse_foods_table(db)
        # Reload DataMatcher with updated tables
        self.matcher = DataMatcher(self.db, food_fuzzy_match_threshold=95, unit_fuzzy_match_threshold=100)

        # Load recipes from cookn
        _recipe_table = db.get_table("temp_recipe")

        recipes_as_dicts = []
        for _recipe_row in _recipe_table:
            try:
                recipes_as_dicts.append(self._process_recipe_document(_recipe_row, db))

            except Exception as e:
                self.report_entries.append(
                    ReportEntryCreate(
                        report_id=self.report_id,
                        success=False,
                        message="Failed to parse recipe",
                        exception=f"{type(e).__name__}: {e}",
                    )
                )

        recipes = []
        for r in recipes_as_dicts:
            # Clean recipes and re-add ingredient w/ amounts
            ingredients = r["_parsed_ingredients"]
            r = self.clean_recipe_dictionary(r)
            r.recipe_ingredient = ingredients
            recipes.append(r)

        # add recipes and images to database
        results = self.import_recipes_to_database(recipes)
        recipe_lookup = {r.slug: r for r in recipes}
        for slug, recipe_id, status in results:
            if status:
                recipe = recipe_lookup.get(slug)
                if recipe:
                    if recipe.image:
                        self.import_image(slug, recipe.image, recipe_id)
                else:
                    index_len = len(slug.split("-")[-1])
                    recipe = recipe_lookup.get(slug[: -(index_len + 1)])
                    if recipe:
                        self.logger.warning("Duplicate recipe (%s) found! Saved as copy...", recipe.name)
                        if recipe.image:
                            self.import_image(slug, recipe.image, recipe_id)
                    else:
                        self.logger.warning("Failed to lookup recipe! (%s)", slug)

    def _migrate(self) -> None:
        """Migrates recipes from Cook'n cookboop .zip. Also will handle a .zip folder of .zip folders"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

                # Process single zipped cookbook
                if Path(f"{tmpdir}/temp_recipe.dsv").exists():
                    self._process_cookbook(Path(tmpdir))

                # Process a zip folder of zipped cookbooks
                for file in Path(tmpdir).glob("*.zip"):
                    with tempfile.TemporaryDirectory() as tmpdir2:
                        with zipfile.ZipFile(file) as zip_file2:
                            zip_file2.extractall(tmpdir2)

                        self._process_cookbook(Path(tmpdir2))
