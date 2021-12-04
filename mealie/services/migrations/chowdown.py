import tempfile
import zipfile
from pathlib import Path
from uuid import UUID

from mealie.db.database import Database

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, import_image, split_by_comma


class ChowdownMigrator(BaseMigrator):
    def __init__(self, archive: Path, db: Database, session, user_id: int, group_id: UUID):
        super().__init__(archive, db, session, user_id, group_id)

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

            for slug, status in results:
                if status:
                    try:
                        original_image = recipe_lookup.get(slug).image
                        cd_image = image_dir.joinpath(original_image)
                    except StopIteration:
                        continue
                    if cd_image:
                        import_image(cd_image, slug)
