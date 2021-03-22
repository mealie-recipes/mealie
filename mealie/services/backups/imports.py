import json
import shutil
import zipfile
from pathlib import Path
from typing import Callable, List

from mealie.core.config import BACKUP_DIR, IMG_DIR, TEMP_DIR
from mealie.db.database import db
from mealie.schema.recipe import Recipe
from mealie.schema.restore import GroupImport, RecipeImport, SettingsImport, ThemeImport, UserImport
from mealie.schema.settings import SiteSettings
from mealie.schema.theme import SiteTheme
from mealie.schema.user import UpdateGroup, UserInDB
from pydantic.main import BaseModel
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
        recipe_dir: Path = self.import_dir.joinpath("recipes")
        imports = []
        successful_imports = []

        recipes = ImportDatabase.read_models_file(
            file_path=recipe_dir, model=Recipe, single_file=False, migrate=ImportDatabase._recipe_migration
        )

        for recipe in recipes:
            recipe: Recipe

            import_status = self.import_model(
                db_table=db.recipes,
                model=recipe,
                return_model=RecipeImport,
                name_attr="name",
                search_key="slug",
                slug=recipe.slug,
            )

            if import_status.status:
                successful_imports.append(recipe.slug)

            imports.append(import_status)

        self._import_images(successful_imports)

        return imports

    @staticmethod
    def _recipe_migration(recipe_dict: dict) -> dict:
        if recipe_dict.get("categories", False):
            recipe_dict["recipeCategory"] = recipe_dict.get("categories")
            del recipe_dict["categories"]
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
        themes = ImportDatabase.read_models_file(themes_file, SiteTheme)
        theme_imports = []

        for theme in themes:
            if theme.name == "default":
                continue

            import_status = self.import_model(
                db_table=db.themes,
                model=theme,
                return_model=ThemeImport,
                name_attr="name",
                search_key="name",
            )

            theme_imports.append(import_status)

        return theme_imports

    def import_settings(self):  #! Broken
        settings_file = self.import_dir.joinpath("settings", "settings.json")
        settings = ImportDatabase.read_models_file(settings_file, SiteSettings)
        settings = settings[0]

        try:
            db.settings.update(self.session, 1, settings.dict())
            import_status = SettingsImport(name="Site Settings", status=True)

        except Exception as inst:
            self.session.rollback()
            import_status = SettingsImport(name="Site Settings", status=False, exception=str(inst))

        return [import_status]

    def import_groups(self):
        groups_file = self.import_dir.joinpath("groups", "groups.json")
        groups = ImportDatabase.read_models_file(groups_file, UpdateGroup)
        group_imports = []

        for group in groups:
            import_status = self.import_model(db.groups, group, GroupImport, search_key="name")
            group_imports.append(import_status)

        return group_imports

    def import_users(self):
        users_file = self.import_dir.joinpath("users", "users.json")
        users = ImportDatabase.read_models_file(users_file, UserInDB)
        user_imports = []
        for user in users:
            if user.id == 1:  # Update Default User
                db.users.update(self.session, 1, user.dict())
                import_status = UserImport(name=user.full_name, status=True)
                user_imports.append(import_status)
                continue

            import_status = self.import_model(
                db_table=db.users,
                model=user,
                return_model=UserImport,
                name_attr="full_name",
                search_key="email",
            )

            user_imports.append(import_status)

        return user_imports

    @staticmethod
    def read_models_file(file_path: Path, model: BaseModel, single_file=True, migrate: Callable = None):
        """A general purpose function that is used to process a backup `.json` file created by mealie
        note that if the file doesn't not exists the function will return any empty list

        Args:
            file_path (Path): The path to the .json file or directory
            model (BaseModel): The pydantic model that will be created from the .json file entries
            single_file (bool, optional): If true, the json data will be treated as list, if false it will use glob style matches and treat each file as its own entry. Defaults to True.
            migrate (Callable, optional): A migrate function that will be called on the data prior to creating a model. Defaults to None.

        Returns:
            [type]: [description]
        """
        if not file_path.exists():
            return []

        if single_file:
            with open(file_path, "r") as f:
                file_data = json.loads(f.read())

            if migrate:
                file_data = [migrate(x) for x in file_data]

            return [model(**g) for g in file_data]

        all_models = []
        for file in file_path.glob("*.json"):
            with open(file, "r") as f:
                file_data = json.loads(f.read())

            if migrate:
                file_data = migrate(file_data)

            all_models.append(model(**file_data))

        return all_models

    def import_model(self, db_table, model, return_model, name_attr="name", search_key="id", **kwargs):
        """A general purpose function used to insert a list of pydantic modelsi into the database.
        The assumption at this point is that the models that are inserted. If self.force_imports is true
        any existing entries will be removed prior to creation

        Args:
            db_table ([type]): A database table like `db.users`
            model ([type]): The Pydantic model that matches the database
            return_model ([type]): The return model that will be used for the 'report'
            name_attr (str, optional): The name property on the return model. Defaults to "name".
            search_key (str, optional): The key used to identify if an the entry already exists. Defaults to "id"
            **kwargs (): Any kwargs passed will be used to set attributes on the `return_model`

        Returns:
            [type]: Returns the `return_model` specified.
        """
        model_name = getattr(model, name_attr)
        search_value = getattr(model, search_key)

        item = db_table.get(self.session, search_value, search_key)
        if item:
            if self.force_imports:
                primary_key = getattr(item, db_table.primary_key)
                db_table.delete(self.session, primary_key)
            else:
                return return_model(
                    name=model_name,
                    status=False,
                    exception=f"Table entry with matching '{search_key}': '{search_value}' exists",
                )

        try:
            db_table.create(self.session, model.dict())
            import_status = return_model(name=model_name, status=True)

        except Exception as inst:
            self.session.rollback()
            import_status = return_model(name=model_name, status=False, exception=str(inst))

        for key, value in kwargs.items():
            setattr(return_model, key, value)

        return import_status

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
    import_session = ImportDatabase(session, archive, force_import)

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

    return data
