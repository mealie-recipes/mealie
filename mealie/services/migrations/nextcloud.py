import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from slugify import slugify

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, glob_walker, import_image, split_by_comma


@dataclass
class NextcloudDir:
    name: str
    recipe: dict
    image: Path | None

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
                recipe = self.clean_recipe_dictionary(nc_dir.recipe)
                all_recipes.append(recipe)

            all_statuses = self.import_recipes_to_database(all_recipes)

            for slug, recipe_id, status in all_statuses:
                if status:
                    nc_dir = nextcloud_dirs[slug]
                    if nc_dir.image:
                        import_image(nc_dir.image, recipe_id)


def parse_time(time: str) -> str:
    """Parses a Nextcloud time string in the format 'PT{hours}H{minutes}M{seconds}S'"""

    # TODO: make singular and plural translatable
    hours = {"singular": "hour", "plural": "hours", "exp": r"\d+(?=H)"}
    minutes = {"singular": "minute", "plural": "minutes", "exp": r"\d+(?=M)"}
    seconds = {"singular": "second", "plural": "seconds", "exp": r"\d+(?=S)"}

    return_strings: list[str] = []
    for time_part in [hours, minutes, seconds]:
        val_search = re.search(time_part["exp"], time)
        if not val_search:
            continue
        val = val_search.group()
        if val == "0":
            continue
        return_strings.append(f'{val} {time_part["singular"] if val == "1" else time_part["plural"]}')

    return " ".join(return_strings) if return_strings else time
