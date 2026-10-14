import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from slugify import slugify

from mealie.schema.reports.reports import ReportEntryCreate

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, glob_walker, split_by_comma


@dataclass
class NextcloudDir:
    name: str
    recipe: dict
    image: Path | None = None

    @property
    def slug(self):
        return slugify(self.recipe.get("name"))

    @classmethod
    def from_dir(cls, dir: Path):
        try:
            json_file = next(dir.glob("*.json"))
        except StopIteration:
            return None

        image_path = next((path for path in dir.glob("full.*") if path.is_file()), dir / "full")
        image_file = image_path if image_path.is_file() else None

        return cls(name=dir.name, recipe=MigrationReaders.json(json_file), image=image_file)


class NextcloudMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "nextcloud"

        self.key_aliases = [
            MigrationAlias(key="tags", alias="keywords", func=split_by_comma),
            MigrationAlias(key="orgURL", alias="url", func=None),
            MigrationAlias(key="totalTime", alias="totalTime", func=None),
            MigrationAlias(key="prepTime", alias="prepTime", func=None),
            MigrationAlias(key="performTime", alias="cookTime", func=None),
        ]

    @classmethod
    def get_zip_base_path(cls, path: Path) -> Path:
        potential_path = super().get_zip_base_path(path)
        if path == potential_path:
            return path

        # make sure we didn't accidentally open a recipe dir
        if (potential_path / "recipe.json").exists():
            return path
        else:
            return potential_path

    def _migrate(self) -> None:
        # Unzip File into temp directory

        # get potential recipe dirs
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            base_dir = self.get_zip_base_path(Path(tmpdir))
            potential_recipe_dirs = glob_walker(base_dir, glob_str="**/[!.]*.json", return_parent=True)
            nextcloud_dirs = [y for x in potential_recipe_dirs if (y := NextcloudDir.from_dir(x))]

            all_recipes = []
            source_dirs = []
            for nc_dir in nextcloud_dirs:
                try:
                    recipe = self.clean_recipe_dictionary(nc_dir.recipe)
                    all_recipes.append(recipe)
                    source_dirs.append(nc_dir)
                except Exception as e:
                    self.logger.exception(e)
                    self.report_entries.append(
                        ReportEntryCreate(
                            report_id=self.report_id,
                            success=False,
                            message=f"Failed to import {nc_dir.name}",
                            exception=f"{e.__class__.__name__}: {e}",
                        )
                    )

            all_statuses = self.import_recipes_to_database(all_recipes)

            for (slug, recipe_id, status), nc_dir in zip(all_statuses, source_dirs, strict=True):
                if status and nc_dir.image:
                    self.import_image(slug, nc_dir.image, recipe_id, extraction_root=base_dir)
