from pathlib import Path
from typing import Optional
from mealie.schema.migration import MigrationImport
from mealie.services.migrations import helpers
from mealie.services.migrations._migration_base import MigrationAlias, MigrationBase
from mealie.services.scraper.scraper import create_from_url
from sqlalchemy.orm.session import Session


class CsvMigration(MigrationBase):
    key_aliases: Optional[list[MigrationAlias]] = [
        MigrationAlias(key="tags", alias="keywords", func=helpers.split_by_comma),
        MigrationAlias(key="org_url", alias="url", func=None),
    ]


def migrate(session: Session, csv_path: Path, max_rows=10) -> list[MigrationImport]:
    csv_migration = CsvMigration(migration_file=csv_path, session=session)

    batch_size = 10
    all_recipes = []
    c = 0
    with csv_migration.temp_dir as dir:
        csv_dir = Path(dir)
        for f in csv_dir.glob("*.*sv"):
            # TODO: the generator gets wrapped in a list to provide feedback on the import size,
            # as we currently need to limit the max. imports
            cur_csvs = list(csv_migration.csv_reader(csv_file=f))
            # Temporarily check the length
            for row in cur_csvs[:max_rows]:
                # Scrape the recipe
                recipe = create_from_url(row["url"])

                if not recipe or recipe.name is None:
                    continue
                # Keep count
                c += 1
                # Set the tags and categories
                recipe.tags = row["tags"]
                recipe.recipe_category = row["categories"]
                # Save it
                all_recipes.append(recipe)
                # Flush the Buffer
                if c >= batch_size:
                    csv_migration.import_recipes_to_database(all_recipes)
                    # Clear the buffer
                    all_recipes = []
                    c = 0
    # Import the rest
    if all_recipes:
        csv_migration.import_recipes_to_database(all_recipes)
    if len(cur_csvs) > max_rows:
        # TODO: this needs to be removed w/ the async queue
        err = f"Can only import {max_rows} recipes at once. Please reduce the import size to 10 per zipped CSV!"
        csv_migration.migration_report.append(MigrationImport(slug="", name=err, status=False, exception=err))
    # If this were a generator, we could return partial results
    return csv_migration.migration_report
