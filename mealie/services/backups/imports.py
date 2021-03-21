import json
import shutil
import zipfile
from pathlib import Path
from typing import List

from fastapi.logger import logger
from mealie.core.config import BACKUP_DIR, IMG_DIR, TEMP_DIR
from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.recipe import Recipe
from mealie.schema.restore import GroupImport, RecipeImport, SettingsImport, ThemeImport, UserImport
from mealie.schema.theme import SiteTheme
from mealie.schema.user import UpdateGroup, UserInDB
from sqlalchemy.orm.session import Session


class ImportDatabase:
    def __init__(
        self,
        session: Session,
        zip_archive: str,
        force_import: bool = False,
    ) -> None:
        """Import a database.zip file exported from mealie.

        Args:
            session (Session): SqlAlchemy Session
            zip_archive (str): The filename contained in the backups directory
            force_import (bool, optional): Force import will update all existing recipes. If False existing recipes are skipped. Defaults to False.

        Raises:
            Exception: If the zip file does not exists an exception raise.
        """
        self.session = session
        self.archive = BACKUP_DIR.joinpath(zip_archive)
        self.force_imports = force_import

        if self.archive.is_file():
            self.import_dir = TEMP_DIR.joinpath("active_import")
            self.import_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.archive, "r") as zip_ref:
                zip_ref.extractall(self.import_dir)
            pass
        else:
            raise Exception("Import file does not exist")

    def import_recipes(self):
        session = create_session()
        recipe_dir: Path = self.import_dir.joinpath("recipes")

        imports = []
        successful_imports = []

        for recipe in recipe_dir.glob("*.json"):
            with open(recipe, "r") as f:
                recipe_dict = json.loads(f.read())
                recipe_dict = ImportDatabase._recipe_migration(recipe_dict)
            try:
                if recipe_dict.get("categories", False):
                    recipe_dict["recipeCategory"] = recipe_dict.get("categories")
                    del recipe_dict["categories"]

                recipe_obj = Recipe(**recipe_dict)
                db.recipes.create(session, recipe_obj.dict())
                import_status = RecipeImport(name=recipe_obj.name, slug=recipe_obj.slug, status=True)
                imports.append(import_status)
                successful_imports.append(recipe.stem)
                logger.info(f"Imported: {recipe.stem}")

            except Exception as inst:
                logger.error(inst)
                logger.info(f"Failed Import: {recipe.stem}")
                import_status = RecipeImport(
                    name=recipe.stem,
                    slug=recipe.stem,
                    status=False,
                    exception=str(inst),
                )
                imports.append(import_status)

        self._import_images(successful_imports)

        return imports

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
                recipe_dict["tags"] = [tag for tag in recipe_dict["tags"] if not tag == ""]
        except:
            pass

        try:
            if "" in recipe_dict["categories"]:
                recipe_dict["categories"] = [cat for cat in recipe_dict["categories"] if not cat == ""]
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
        theme_imports = []
        with open(themes_file, "r") as f:
            themes: list[dict] = json.loads(f.read())
        for theme in themes:
            if theme.get("name") == "default":
                continue
            new_theme = SiteTheme(**theme)
            try:

                db.themes.create(self.session, new_theme.dict())
                theme_imports.append(ThemeImport(name=new_theme.name, status=True))
            except Exception as inst:
                logger.info(f"Unable Import Theme {new_theme.name}")
                theme_imports.append(ThemeImport(name=new_theme.name, status=False, exception=str(inst)))

        return theme_imports

    def import_settings(self):
        settings_file = self.import_dir.joinpath("settings", "settings.json")
        settings_imports = []

        with open(settings_file, "r") as f:
            settings: dict = json.loads(f.read())

            name = settings.get("name")

            try:
                db.settings.update(self.session, name, settings)
                import_status = SettingsImport(name=name, status=True)

            except Exception as inst:
                import_status = SettingsImport(name=name, status=False, exception=str(inst))

            settings_imports.append(import_status)
        return settings_imports

    def import_groups(self):
        groups_file = self.import_dir.joinpath("groups", "groups.json")
        group_imports = []

        with open(groups_file, "r") as f:
            groups = [UpdateGroup(**g) for g in json.loads(f.read())]

        for group in groups:
            item = db.groups.get(self.session, group.name, "name")
            if item:
                import_status = GroupImport(name=group.name, status=False, exception="Group Exists")
                group_imports.append(import_status)
                continue
            try:
                db.groups.create(self.session, group.dict())
                import_status = GroupImport(name=group.name, status=True)

            except Exception as inst:
                import_status = GroupImport(name=group.name, status=False, exception=str(inst))

            group_imports.append(import_status)

        print(group_imports)
        return group_imports

    def import_users(self):
        users_file = self.import_dir.joinpath("users", "users.json")
        user_imports = []

        with open(users_file, "r") as f:
            users = [UserInDB(**g) for g in json.loads(f.read())]

        for user in users:
            if user.id == 1:
                db.users.update(self.session, 1, user.dict())
                import_status = UserImport(name=user.full_name, status=True)
                user_imports.append(import_status)
                continue

            item = db.users.get(self.session, user.email, "email")
            if item:
                import_status = UserImport(name=user.full_name, status=False, exception="User Email Exists")
                user_imports.append(import_status)
                continue

            try:
                db.users.create(self.session, user.dict())
                import_status = UserImport(name=user.full_name, status=True)

            except Exception as inst:
                import_status = UserImport(name=user.full_name, status=False, exception=str(inst))

            user_imports.append(import_status)

        return user_imports

    def clean_up(self):
        shutil.rmtree(TEMP_DIR)


def import_database(
    session: Session,
    archive,
    import_recipes=True,
    import_settings=True,
    import_themes=True,
    import_users=True,
    import_groups=True,
    force_import: bool = False,
    rebase: bool = False,
):
    import_session = ImportDatabase(session, archive)

    recipe_report = []
    if import_recipes:
        recipe_report = import_session.import_recipes()

    settings_report = []
    if import_settings:
        settings_report = import_session.import_settings()

    theme_report = []
    if import_themes:
        theme_report = import_session.import_themes()

    group_report = []
    if import_groups:
        print("Import Groups")
        group_report = import_session.import_groups()

    user_report = []
    if import_users:
        user_report = import_session.import_users()

    import_session.clean_up()

    data = {
        "recipeImports": recipe_report,
        "settingsImports": settings_report,
        "themeImports": theme_report,
        "groupImports": group_report,
        "userImports": user_report,
    }

    print(data)

    return data
