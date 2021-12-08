import base64
import io
import json
import tempfile
import zipfile
from gzip import GzipFile
from pathlib import Path
from pprint import pprint
from uuid import UUID

import regex as re
from slugify import slugify

from mealie.db.database import Database
from mealie.schema.recipe import RecipeNote
from mealie.services.migrations.utils.migration_alias import MigrationAlias
from mealie.services.migrations.utils.migration_helpers import import_image

from ._migration_base import BaseMigrator


def paprika_recipes(file: Path):
    """Yields all recipes inside the export file as JSON"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(file) as zip_file:
            zip_file.extractall(tmpdir)

        for name in Path(tmpdir).glob("**/[!.]*.paprikarecipe"):
            with open(name, "rb") as fd:
                with GzipFile("r", fileobj=fd) as recipe_json:
                    recipe = json.load(recipe_json)
                    yield recipe


class PaprikaMigrator(BaseMigrator):
    def __init__(self, archive: Path, db: Database, session, user_id: int, group_id: UUID):
        super().__init__(archive, db, session, user_id, group_id)

        re_num_list = re.compile(r"^\d+\.\s")

        self.key_aliases = [
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=lambda x: x.split("\n")),
            MigrationAlias(key="orgUrl", alias="source_url", func=None),
            MigrationAlias(key="performTime", alias="cook_time", func=None),
            MigrationAlias(key="recipeYield", alias="servings", func=None),
            MigrationAlias(key="image", alias="image_url", func=None),
            MigrationAlias(key="dateAdded", alias="created", func=lambda x: x[: x.find(" ")]),
            MigrationAlias(
                key="notes",
                alias="notes",
                func=lambda x: [z for z in [RecipeNote(title="", text=x) if x else None] if z],
            ),
            MigrationAlias(
                key="recipeCategory",
                alias="categories",
                func=self.helpers.get_or_set_category,
            ),
            MigrationAlias(
                key="recipeInstructions",
                alias="directions",
                func=lambda x: [{"text": re.sub(re_num_list, "", s)} for s in x.split("\n\n")],
            ),
        ]

    def _migrate(self) -> None:
        recipe_image_urls = {}

        recipes = []
        for recipe in paprika_recipes(self.archive):
            if "name" not in recipe:
                continue

            recipe_model = self.clean_recipe_dictionary(recipe)

            if "photo_data" in recipe:
                recipe_image_urls[slugify(recipe["name"])] = recipe["photo_data"]

            recipes.append(recipe_model)

        pprint(recipe_image_urls)

        results = self.import_recipes_to_database(recipes)

        for slug, status in results:
            if not status:
                continue

            try:
                image = io.BytesIO(base64.b64decode(recipe_image_urls[slug]))
                with tempfile.NamedTemporaryFile(suffix=".jpeg") as temp_file:
                    temp_file.write(image.read())
                    path = Path(temp_file.name)
                    import_image(path, slug)
            except Exception as e:
                self.logger.error(f"Failed to download image for {slug}: {e}")
