import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from slugify import slugify

from mealie.db.database import Database

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, glob_walker, import_image, split_by_comma


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

        return cls(name=dir.name, recipe=MigrationReaders.json(json_file), image=image_file)


class NextcloudMigrator(BaseMigrator):
    def __init__(self, archive: Path, db: Database, session, user_id: int, group_id: int):
        super().__init__(archive, db, session, user_id, group_id)

        self.key_aliases = [
            MigrationAlias(key="tags", alias="keywords", func=split_by_comma),
            MigrationAlias(key="org_url", alias="url", func=None),
        ]

    def _migrate(self) -> None:
        # Unzip File into temp directory

        # get potential recipe dirs
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            potential_recipe_dirs = glob_walker(Path(tmpdir), glob_str="**/[!.]*.json", return_parent=True)
            nextcloud_dirs = {y.slug: y for x in potential_recipe_dirs if (y := NextcloudDir.from_dir(x))}

            all_recipes = []
            for _, nc_dir in nextcloud_dirs.items():
                recipe = self.clean_recipe_dictionary(nc_dir.recipe)
                all_recipes.append(recipe)

            all_statuses = self.import_recipes_to_database(all_recipes)

            for slug, status in all_statuses:
                if status:
                    nc_dir: NextcloudDir = nextcloud_dirs[slug]
                    if nc_dir.image:
                        import_image(nc_dir.image, nc_dir.slug)
