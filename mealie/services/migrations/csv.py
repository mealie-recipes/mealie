from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os 
import glob
from mealie.schema.migration import MigrationImport
from mealie.services.migrations import helpers
from mealie.services.migrations._migration_base import MigrationAlias, MigrationBase
from mealie.services.scraper.scraper import create_from_url
from slugify import slugify
from sqlalchemy.orm.session import Session


class CsvMigration(MigrationBase):
    key_aliases: Optional[list[MigrationAlias]] = [
        MigrationAlias(key="tags", alias="keywords", func=helpers.split_by_comma),
        MigrationAlias(key="org_url", alias="url", func=None),
    ]


def migrate(session: Session, csv_path: Path) -> list[MigrationImport]:
    csv_migration = CsvMigration(migration_file=csv_path, session=session)

    all_recipes = []
    with csv_migration.temp_dir as dir:
        csv_dir = Path(dir)
        for f in csv_dir.glob("*.*sv"):
            for row in csv_migration.csv_reader(csv_file=f):
                print(row)
                # Scrape the recipe
                recipe = create_from_url(row["url"])
                if not recipe or recipe.name is None:
                    continue
                # Set the tags and categories
                recipe.tags = row["tags"]
                recipe.recipe_category = row["categories"]
                # Save it
                all_recipes.append(recipe)
            # Import
            csv_migration.import_recipes_to_database(all_recipes)

    return csv_migration.migration_report
