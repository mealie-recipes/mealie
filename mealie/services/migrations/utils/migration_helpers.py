import json
from pathlib import Path

import yaml

from mealie.services.image import image


class MigrationReaders:
    @staticmethod
    def json(json_file: Path) -> dict:
        with open(json_file, "r") as f:
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
        with open(yaml_file, "r") as f:
            contents = f.read().split("---")
            recipe_data = {}
            for _, document in enumerate(contents):

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


def import_image(src: Path, dest_slug: str):
    """Read the successful migrations attribute and for each import the image
    appropriately into the image directory. Minification is done in mass
    after the migration occurs.
    """
    image.write_image(dest_slug, src, extension=src.suffix)
