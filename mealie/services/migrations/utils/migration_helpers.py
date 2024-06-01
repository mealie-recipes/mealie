import json
from datetime import timedelta
from pathlib import Path
from typing import cast

import isodate
import yaml
from PIL import UnidentifiedImageError
from pydantic import UUID4

from mealie.services.recipe.recipe_data_service import RecipeDataService


class MigrationReaders:
    @staticmethod
    def json(json_file: Path) -> dict:
        with open(json_file) as f:
            return json.loads(f.read())

    @staticmethod
    def yaml(yaml_file: Path) -> dict:
        """A helper function to read in a yaml file from a Path. This assumes that the
        first yaml document is the recipe data and the second, if exists, is the description.

        Args:
            yaml_file (Path): Path to yaml file

        Returns:
            dict: representing the yaml file as a dictionary
        """
        with open(yaml_file) as f:
            contents = f.read().split("---")
            recipe_data = {}
            for document in contents:
                # Check if None or Empty String
                if document is None or document == "":
                    continue

                # Check if 'title:' present
                elif "title:" in document:
                    recipe_data.update(yaml.safe_load(document))

                else:
                    recipe_data["description"] = document

        return recipe_data


def split_by_comma(tag_string: str):
    """Splits a single string by ',' performs a line strip and then title cases the resulting string

    Args:
        tag_string (str): [description]

    Returns:
        [type]: [description]
    """
    if not isinstance(tag_string, str):
        return None
    return [x.title().lstrip() for x in tag_string.split(",") if x != ""]


def split_by_semicolon(input: str):
    """Splits a single string by ';', performs a line strip removes empty strings"""

    if not isinstance(input, str):
        return None
    return [x.strip() for x in input.split(";") if x]


def split_by_line_break(input: str):
    """Splits a single string by line break, performs a line strip removes empty strings"""
    if not isinstance(input, str):
        return None
    return [x.strip() for x in input.split("\n") if x]


def glob_walker(directory: Path, glob_str: str, return_parent=True) -> list[Path]:  # TODO:
    """A Helper function that will return the glob matches for the temporary directotry
    that was unpacked and passed in as the `directory` parameter. If `return_parent` is
    True the return Paths will be the parent directory for the file that was matched. If
    false the file itself will be returned.

    Args:
        directory (Path): Path to search directory
        glob_str ([type]): glob style match string
        return_parent (bool, optional): To return parent directory of match. Defaults to True.

    Returns:
        list[Path]:
    """
    directory = directory if isinstance(directory, Path) else Path(directory)
    matches = []
    for match in directory.glob(glob_str):
        if return_parent:
            matches.append(match.parent)
        else:
            matches.append(match)

    return matches


def import_image(src: str | Path, recipe_id: UUID4):
    """Read the successful migrations attribute and for each import the image
    appropriately into the image directory. Minification is done in mass
    after the migration occurs.
    """

    if isinstance(src, str):
        src = Path(src)

    if not src.exists():
        return

    data_service = RecipeDataService(recipe_id=recipe_id)

    try:
        data_service.write_image(src, src.suffix)
    except UnidentifiedImageError:
        return


async def scrape_image(image_url: str, recipe_id: UUID4):
    """Read the successful migrations attribute and for each scrape the image
    appropriately into the image directory. Minification is done in mass
    after the migration occurs.
    """

    if not isinstance(image_url, str):
        return

    data_service = RecipeDataService(recipe_id=recipe_id)

    try:
        await data_service.scrape_image(image_url)
    except UnidentifiedImageError:
        return


def parse_iso8601_duration(time: str | None) -> str:
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
        except isodate.ISO8601Error:
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
