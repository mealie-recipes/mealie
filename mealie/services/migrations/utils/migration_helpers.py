import json
from pathlib import Path

import yaml
from PIL import UnidentifiedImageError
from pydantic import UUID4

from mealie.core import root_logger
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


def safe_local_path(candidate: str | Path, root: Path) -> Path | None:
    """
    Returns the resolved path only if it is safely contained within root.

    Returns ``None`` for any path that would escape the root directory,
    including ``../../`` traversal sequences and absolute paths outside root.
    Symlinks are followed by ``resolve()``, so a symlink pointing outside root
    is also rejected.
    """
    try:
        # OSError: symlink resolution failure; ValueError: null bytes on some platforms
        resolved = Path(candidate).resolve()
        if resolved.is_relative_to(root.resolve()):
            return resolved
    except OSError, ValueError:
        pass
    return None


def import_image(src: str | Path, recipe_id: UUID4, extraction_root: Path | None = None) -> Path | None:
    """Import a local image file into the recipe image directory.

    Returns the path the image was written to, or `None` if there was nothing to import.

    May raise an UnidentifiedImageError if the file is not a recognised format.

    If extraction_root is provided, the src path must be contained within it.
    Paths that escape the extraction_root are silently rejected to prevent
    arbitrary local file reads via archive-controlled image paths.
    """

    if isinstance(src, str):
        src = Path(src)

    if extraction_root is not None:
        if safe_local_path(src, extraction_root) is None:
            root_logger.get_logger().warning(
                "Rejected image path outside extraction root: %s (root: %s)", src, extraction_root
            )
            return None

    if not src.exists():
        return None

    data_service = RecipeDataService(recipe_id=recipe_id)
    return data_service.write_image(src, src.suffix)


async def scrape_image(image_url: str, recipe_id: UUID4) -> Path | None:
    """Read the successful migrations attribute and for each scrape the image
    appropriately into the image directory. Minification is done in mass
    after the migration occurs.

    Returns the path the image was written to, or `None` if nothing was downloaded.
    """

    if not isinstance(image_url, str):
        return None

    data_service = RecipeDataService(recipe_id=recipe_id)

    try:
        return await data_service.scrape_image(image_url)
    except UnidentifiedImageError:
        return None
