import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Optional

import yaml
from pydantic import BaseModel

from mealie.core import root_logger
from mealie.db.database import db
from mealie.schema.admin import MigrationImport
from mealie.schema.recipe import Recipe
from mealie.schema.user.user import PrivateUser
from mealie.services.image import image
from mealie.services.scraper import cleaner
from mealie.utils.unzip import unpack_zip

logger = root_logger.get_logger()


class MigrationAlias(BaseModel):
    """A datatype used by MigrationBase to pre-process a recipe dictionary to rewrite
    the alias key in the dictionary, if it exists, to the key. If set a `func` attribute
    will be called on the value before assigning the value to the new key
    """

    key: str
    alias: str
    func: Optional[Callable] = None


class MigrationBase(BaseModel):
    migration_report: list[MigrationImport] = []
    migration_file: Path
    session: Optional[Any]
    key_aliases: Optional[list[MigrationAlias]]

    user: PrivateUser

    @property
    def temp_dir(self) -> TemporaryDirectory:
        """unpacks the migration_file into a temporary directory
        that can be used as a context manager.

        Returns:
            TemporaryDirectory:
        """
        return unpack_zip(self.migration_file)

    @staticmethod
    def json_reader(json_file: Path) -> dict:
        with open(json_file, "r") as f:
            return json.loads(f.read())

    @staticmethod
    def yaml_reader(yaml_file: Path) -> dict:
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
            for x, document in enumerate(contents):

                # Check if None or Empty String
                if document is None or document == "":
                    continue

                # Check if 'title:' present
                elif "title:" in document:
                    recipe_data.update(yaml.safe_load(document))

                else:
                    recipe_data["description"] = document

        return recipe_data

    @staticmethod
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

    @staticmethod
    def import_image(src: Path, dest_slug: str):
        """Read the successful migrations attribute and for each import the image
        appropriately into the image directory. Minification is done in mass
        after the migration occurs.
        """
        image.write_image(dest_slug, src, extension=src.suffix)

    def rewrite_alias(self, recipe_dict: dict) -> dict:
        """A helper function to reassign attributes by an alias using a list
        of MigrationAlias objects to rewrite the alias attribute found in the recipe_dict
        to a

        Args:
            recipe_dict (dict): [description]
            key_aliases (list[MigrationAlias]): [description]

        Returns:
            dict: [description]
        """
        if not self.key_aliases:
            return recipe_dict

        for alias in self.key_aliases:
            try:
                prop_value = recipe_dict.pop(alias.alias)
            except KeyError:
                logger.info(f"Key {alias.alias} Not Found. Skipping...")
                continue

            if alias.func:
                prop_value = alias.func(prop_value)

            recipe_dict[alias.key] = prop_value

        return recipe_dict

    def clean_recipe_dictionary(self, recipe_dict) -> Recipe:
        """
        Calls the rewrite_alias function and the Cleaner.clean function on a
        dictionary and returns the result unpacked into a Recipe object
        """
        recipe_dict = self.rewrite_alias(recipe_dict)
        recipe_dict = cleaner.clean(recipe_dict, url=recipe_dict.get("org_url", None))

        return Recipe(**recipe_dict)

    def import_recipes_to_database(self, validated_recipes: list[Recipe]) -> None:
        """
        Used as a single access point to process a list of Recipe objects into the
        database in a predictable way. If an error occurs the session is rolled back
        and the process will continue. All import information is appended to the
        'migration_report' attribute to be returned to the frontend for display.

        Args:
            validated_recipes (list[Recipe]):
        """

        for recipe in validated_recipes:

            recipe.user_id = self.user.id
            recipe.group_id = self.user.group_id

            exception = ""
            status = False
            try:
                db.recipes.create(self.session, recipe.dict())
                status = True

            except Exception as inst:
                exception = inst
                logger.error(inst)
                self.session.rollback()

            import_status = MigrationImport(slug=recipe.slug, name=recipe.name, status=status, exception=str(exception))
            self.migration_report.append(import_status)
