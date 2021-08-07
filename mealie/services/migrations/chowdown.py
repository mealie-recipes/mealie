from pathlib import Path
from typing import Optional

from mealie.core.config import app_dirs
from mealie.schema.admin import MigrationImport
from mealie.services.migrations import helpers
from mealie.services.migrations._migration_base import MigrationAlias, MigrationBase
from sqlalchemy.orm.session import Session


class ChowdownMigration(MigrationBase):
    key_aliases: Optional[list[MigrationAlias]] = [
        MigrationAlias(key="name", alias="title", func=None),
        MigrationAlias(key="recipeIngredient", alias="ingredients", func=None),
        MigrationAlias(key="recipeInstructions", alias="directions", func=None),
        MigrationAlias(key="tags", alias="tags", func=helpers.split_by_comma),
    ]


def migrate(session: Session, zip_path: Path) -> list[MigrationImport]:
    cd_migration = ChowdownMigration(migration_file=zip_path, session=session)

    with cd_migration.temp_dir as dir:
        chow_dir = next(Path(dir).iterdir())
        image_dir = app_dirs.TEMP_DIR.joinpath(chow_dir, "images")
        recipe_dir = app_dirs.TEMP_DIR.joinpath(chow_dir, "_recipes")

        recipes_as_dicts = [y for x in recipe_dir.glob("*.md") if (y := ChowdownMigration.yaml_reader(x)) is not None]

        recipes = [cd_migration.clean_recipe_dictionary(x) for x in recipes_as_dicts]

        cd_migration.import_recipes_to_database(recipes)

        recipe_lookup = {r.slug: r for r in recipes}

        for report in cd_migration.migration_report:
            if report.status:
                try:
                    original_image = recipe_lookup.get(report.slug).image
                    cd_image = image_dir.joinpath(original_image)
                except StopIteration:
                    continue
                if cd_image:
                    ChowdownMigration.import_image(cd_image, report.slug)

    return cd_migration.migration_report
