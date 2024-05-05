import tempfile
import zipfile
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import cast

import isodate
from isodate.isoerror import ISO8601Error
from slugify import slugify

from mealie.schema.reports.reports import ReportEntryCreate

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, glob_walker, import_image, split_by_comma


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

        try:  # TODO: There's got to be a better way to do this.
            image_file = next(dir.glob("full.*"))
        except StopIteration:
            image_file = None

        return cls(name=dir.name, recipe=MigrationReaders.json(json_file), image=image_file)


class NextcloudMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "nextcloud"

        self.key_aliases = [
            MigrationAlias(key="tags", alias="keywords", func=split_by_comma),
            MigrationAlias(key="orgURL", alias="url", func=None),
            MigrationAlias(key="totalTime", alias="totalTime", func=parse_time),
            MigrationAlias(key="prepTime", alias="prepTime", func=parse_time),
            MigrationAlias(key="performTime", alias="cookTime", func=parse_time),
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
                try:
                    recipe = self.clean_recipe_dictionary(nc_dir.recipe)
                    all_recipes.append(recipe)
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

            for slug, recipe_id, status in all_statuses:
                if status:
                    nc_dir = nextcloud_dirs[slug]
                    if nc_dir.image:
                        import_image(nc_dir.image, recipe_id)


def parse_time(time: str | None) -> str:
    """
    Parses an ISO8601 duration string

    https://en.wikipedia.org/wiki/ISO_8601#Durations
    """

    if not time:
        return ""
    if time[0] == "P":
        try:
            delta = isodate.parse_duration(time)
            if not isinstance(delta, timedelta):
                return time
        except ISO8601Error:
            return time

    # TODO: make singular and plural translatable
    time_part_map = {
        "days": {"singular": "day", "plural": "days"},
        "hours": {"singular": "hour", "plural": "hours"},
        "minutes": {"singular": "minute", "plural": "minutes"},
        "seconds": {"singular": "second", "plural": "seconds"},
    }

    delta = cast(timedelta, delta)
    time_part_map["days"]["value"] = delta.days
    time_part_map["hours"]["value"] = delta.seconds // 3600
    time_part_map["minutes"]["value"] = (delta.seconds // 60) % 60
    time_part_map["seconds"]["value"] = delta.seconds % 60

    return_strings: list[str] = []
    for value_map in time_part_map.values():
        if not (value := value_map["value"]):
            continue

        unit_key = "singular" if value == 1 else "plural"
        return_strings.append(f"{value} {value_map[unit_key]}")

    return " ".join(return_strings) if return_strings else time
