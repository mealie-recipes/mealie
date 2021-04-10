from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mealie.schema.migration import MigrationImport
from mealie.services.migrations import helpers
from mealie.services.migrations._migration_base import MigrationAlias, MigrationBase
from slugify import slugify
from sqlalchemy.orm.session import Session


@dataclass
class NextcloudDir:
    name: str
    recipe: dict
    image: Optional[Path]

    @property
    def slug(self):
        return slugify(self.recipe.get("name"))

    @classmethod
    def from_dir(cls, dir: Path):
        try:
            json_file = next(dir.glob("*.json"))
        except StopIteration:
            return None

        try:  # TODO: There's got to be a better way to do this.
            image_file = next(dir.glob("full.*"))
        except StopIteration:
            image_file = None

        return cls(name=dir.name, recipe=NextcloudMigration.json_reader(json_file), image=image_file)


class NextcloudMigration(MigrationBase):
    key_aliases: Optional[list[MigrationAlias]] = [
        MigrationAlias(key="tags", alias="keywords", func=helpers.split_by_comma),
        MigrationAlias(key="orgURL", alias="url", func=None),
    ]


def migrate(session: Session, zip_path: Path) -> list[MigrationImport]:

    nc_migration = NextcloudMigration(migration_file=zip_path, session=session)

    with nc_migration.temp_dir as dir:
        potential_recipe_dirs = NextcloudMigration.glob_walker(dir, glob_str="**/[!.]*.json", return_parent=True)

        # nextcloud_dirs = [NextcloudDir.from_dir(x) for x in potential_recipe_dirs]
        nextcloud_dirs = {y.slug: y for x in potential_recipe_dirs if (y := NextcloudDir.from_dir(x))}
        # nextcloud_dirs = {x.slug: x for x in nextcloud_dirs}

        all_recipes = []
        for _, nc_dir in nextcloud_dirs.items():
            recipe = nc_migration.clean_recipe_dictionary(nc_dir.recipe)
            all_recipes.append(recipe)

        nc_migration.import_recipes_to_database(all_recipes)

        for report in nc_migration.migration_report:

            if report.status:
                nc_dir: NextcloudDir = nextcloud_dirs[report.slug]
                if nc_dir.image:
                    NextcloudMigration.import_image(nc_dir.image, nc_dir.slug)

    return nc_migration.migration_report
