import tempfile
import zipfile
from pathlib import Path

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, import_image, split_by_comma


class ChowdownMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "chowdown"

        self.key_aliases = [
            MigrationAlias(key="name", alias="title", func=None),
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=None),
            MigrationAlias(key="recipeInstructions", alias="directions", func=None),
            MigrationAlias(key="tags", alias="tags", func=split_by_comma),
        ]

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            temp_path = Path(tmpdir)

            chow_dir = next(temp_path.iterdir())
            image_dir = temp_path.joinpath(chow_dir, "images")
            recipe_dir = temp_path.joinpath(chow_dir, "_recipes")

            recipes_as_dicts = [y for x in recipe_dir.glob("*.md") if (y := MigrationReaders.yaml(x)) is not None]

            recipes = [self.clean_recipe_dictionary(x) for x in recipes_as_dicts]

            results = self.import_recipes_to_database(recipes)

            recipe_lookup = {r.slug: r for r in recipes}

            for slug, recipe_id, status in results:
                if status:
                    try:
                        r = recipe_lookup.get(slug)

                        if not r:
                            continue

                        if r.image:
                            cd_image = image_dir.joinpath(r.image)
                    except StopIteration:
                        continue
                    if cd_image:
                        import_image(cd_image, recipe_id)
