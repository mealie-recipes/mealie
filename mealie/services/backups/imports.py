import json
import shutil
import zipfile
from logging import error
from pathlib import Path
from typing import List

from app_config import BACKUP_DIR, IMG_DIR, TEMP_DIR
from db.database import db
from models.theme_models import SiteTheme
from services.recipe_services import Recipe
from services.settings_services import SiteSettings
from sqlalchemy.orm.session import Session
from utils.logger import logger


class ImportDatabase:
    def __init__(
        self,
        session: Session,
        zip_archive: str,
        import_recipes: bool = True,
        import_settings: bool = True,
        import_themes: bool = True,
        force_import: bool = False,
        rebase: bool = False,
    ) -> None:
        """Import a database.zip file exported from mealie.

        Args:
            zip_archive (str): The filename contained in the backups directory
            import_recipes (bool, optional): Import Recipes?. Defaults to True.
            import_settings (bool, optional): Determines if settings are imported. Defaults to True.
            import_themes (bool, optional): Determines if themes are imported. Defaults to True.
            force_import (bool, optional): Force import will update all existing recipes. If False existing recipes are skipped. Defaults to False.
            rebase (bool, optional): Rebase will first clear the database and then import Recipes. Defaults to False.

        Raises:
            Exception: If the zip file does not exists an exception raise.
        """
        self.session = session
        self.archive = BACKUP_DIR.joinpath(zip_archive)
        self.imp_recipes = import_recipes
        self.imp_settings = import_settings
        self.imp_themes = import_themes
        self.force_imports = force_import
        self.force_rebase = rebase

        if self.archive.is_file():
            self.import_dir = TEMP_DIR.joinpath("active_import")
            self.import_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.archive, "r") as zip_ref:
                zip_ref.extractall(self.import_dir)
            pass
        else:
            raise Exception("Import file does not exist")

    def run(self):
        report = {}
        if self.imp_recipes:
            report = self.import_recipes()
        if self.imp_settings:
            self.import_settings()
        if self.imp_themes:
            self.import_themes()

        self.clean_up()

        return report if report else None

    def import_recipes(self):
        recipe_dir: Path = self.import_dir.joinpath("recipes")

        successful_imports = []
        failed_imports = []

        for recipe in recipe_dir.glob("*.json"):
            with open(recipe, "r") as f:
                recipe_dict = json.loads(f.read())
                recipe_dict = ImportDatabase._recipe_migration(recipe_dict)
            try:
                recipe_obj = Recipe(**recipe_dict)
                recipe_obj.save_to_db(self.session)
                successful_imports.append(recipe.stem)
                logger.info(f"Imported: {recipe.stem}")
            except Exception as inst:
                logger.error(inst)
                logger.info(f"Failed Import: {recipe.stem}")
                failed_imports.append(recipe.stem)

        self._import_images(successful_imports)

        return {"successful": successful_imports, "failed": failed_imports}

    @staticmethod
    def _recipe_migration(recipe_dict: dict) -> dict:
        try:
            del recipe_dict["_id"]
            del recipe_dict["dateAdded"]
        except:
            pass
        # Migration from list to Object Type Data
        try:
            if "" in recipe_dict["tags"]:
                recipe_dict["tags"] = [
                    tag for tag in recipe_dict["tags"] if not tag == ""
                ]
        except:
            pass

        try:
            if "" in recipe_dict["categories"]:
                recipe_dict["categories"] = [
                    cat for cat in recipe_dict["categories"] if not cat == ""
                ]
        except:
            pass

        if type(recipe_dict["extras"]) == list:
            recipe_dict["extras"] = {}

        return recipe_dict

    def _import_images(self, successful_imports: List[str]):
        image_dir = self.import_dir.joinpath("images")
        for image in image_dir.iterdir():
            if image.stem in successful_imports:
                shutil.copy(image, IMG_DIR)

    def import_themes(self):
        themes_file = self.import_dir.joinpath("themes", "themes.json")

        with open(themes_file, "r") as f:
            themes: list[dict] = json.loads(f.read())
        for theme in themes:
            if theme.get("name") == "default":
                continue
            new_theme = SiteTheme(**theme)
            try:
                db.themes.create(self.session, new_theme.dict())
            except:
                logger.info(f"Unable Import Theme {new_theme.name}")

    def import_settings(self):
        settings_file = self.import_dir.joinpath("settings", "settings.json")

        with open(settings_file, "r") as f:
            settings: dict = json.loads(f.read())

            db.settings.update(self.session, settings)

    def clean_up(self):
        shutil.rmtree(TEMP_DIR)
