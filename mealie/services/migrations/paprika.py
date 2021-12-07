import json
from gzip import GzipFile
from io import BytesIO
from pathlib import Path
from uuid import UUID
from zipfile import ZipFile

import regex as re
from slugify import slugify

from mealie.db.database import Database
from mealie.schema.recipe import RecipeCategory, RecipeNote
from mealie.services.migrations.utils.migration_alias import MigrationAlias

from ._migration_base import BaseMigrator


def paprika_recipes(file: Path):
    """Yields all recipes inside the export file as JSON"""
    with ZipFile(file, "r") as f:
        for name in f.namelist():
            with f.open(name, "r") as inner_file:
                inner_data = BytesIO(inner_file.read())
                with GzipFile("r", fileobj=inner_data) as recipe_json:
                    recipe = json.load(recipe_json)
                    yield recipe


class PaprikaMigrator(BaseMigrator):
    def __init__(self, archive: Path, db: Database, session, user_id: int, group_id: UUID):
        super().__init__(archive, db, session, user_id, group_id)

        re_num_list = re.compile(r"^\d+\.\s")

        self.key_aliases = [
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=lambda x: x.split("\n")),
            MigrationAlias(key="org_url", alias="source_url", func=None),
            MigrationAlias(key="performTime", alias="cook_time", func=None),
            MigrationAlias(key="recipe_yield", alias="servings", func=None),
            MigrationAlias(key="dateAdded", alias="created", func=lambda x: x[: x.find(" ")]),
            MigrationAlias(
                key="notes",
                alias="notes",
                func=lambda x: [z for z in [RecipeNote(title="", text=x) if x else None] if z],
            ),
            # TODO: Recipe Categories currently doesn't work
            MigrationAlias(
                key="recipeCategory",
                alias="categories",
                func=lambda x: [RecipeCategory(name=y, slug=slugify(y)) for y in x],
            ),
            MigrationAlias(
                key="recipeInstructions",
                alias="directions",
                func=lambda x: [{"text": re.sub(re_num_list, "", s)} for s in x.split("\n\n")],
            ),
        ]

    def _migrate(self) -> None:
        recipes = [self.clean_recipe_dictionary(x) for x in paprika_recipes(self.archive) if x.get("name")]

        results = self.import_recipes_to_database(recipes)

        print(results)

        # TODO: Scrape Recipe Images from URLs for successful imports

        # recipe_lookup = {r.slug: r for r in recipes}

        # for slug, status in results:
        #     if status:
        #         try:
        #             original_image = recipe_lookup.get(slug).image
        #             cd_image = image_dir.joinpath(original_image)
        #         except StopIteration:
        #             continue
        #         if cd_image:
        #             import_image(cd_image, slug)
