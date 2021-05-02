import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Union

from jinja2 import Template
from mealie.core import root_logger
from mealie.core.config import app_dirs
from mealie.db.database import db
from mealie.db.db_setup import create_session
from pathvalidate import sanitize_filename
from pydantic.main import BaseModel

logger = root_logger.get_logger()


class ExportDatabase:
    def __init__(self, tag=None, templates=None) -> None:
        """Export a Mealie database. Export interacts directly with class objects and can be used
        with any supported backend database platform. By default tags are timestamps, and no
        Jinja2 templates are rendered


        Args:
            tag ([str], optional): A str to be used as a file tag. Defaults to None.
            templates (list, optional): A list of template file names. Defaults to None.
        """
        if tag:
            export_tag = tag + "_" + datetime.now().strftime("%Y-%b-%d")
        else:
            export_tag = datetime.now().strftime("%Y-%b-%d")

        self.main_dir = app_dirs.TEMP_DIR.joinpath(export_tag)
        self.recipes = self.main_dir.joinpath("recipes")
        self.templates_dir = self.main_dir.joinpath("templates")

        try:
            self.templates = [app_dirs.TEMPLATE_DIR.joinpath(x) for x in templates]
        except Exception:
            self.templates = False
            logger.info("No Jinja2 Templates Registered for Export")

        required_dirs = [
            self.main_dir,
            self.recipes,
            self.templates_dir,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)

    def export_templates(self, recipe_list: list[BaseModel]):
        for template_path in self.templates:
            out_dir = self.templates_dir.joinpath(template_path.name)
            out_dir.mkdir(parents=True, exist_ok=True)

            with open(template_path, "r") as f:
                template = Template(f.read())

            for recipe in recipe_list:
                filename = recipe.slug + template_path.suffix
                out_file = out_dir.joinpath(filename)

                content = template.render(recipe=recipe)

                with open(out_file, "w") as f:
                    f.write(content)

    def export_recipe_dirs(self):
        shutil.copytree(app_dirs.RECIPE_DATA_DIR, self.recipes, dirs_exist_ok=True)

    def export_items(self, items: list[BaseModel], folder_name: str, export_list=True, slug_folder=False):
        items = [x.dict() for x in items]
        out_dir = self.main_dir.joinpath(folder_name)
        out_dir.mkdir(parents=True, exist_ok=True)

        if export_list:
            ExportDatabase._write_json_file(items, out_dir.joinpath(f"{folder_name}.json"))
        else:
            for item in items:
                final_dest = out_dir if not slug_folder else out_dir.joinpath(item.get("slug"))
                filename = sanitize_filename(f"{item.get('slug')}.json")
                ExportDatabase._write_json_file(item, final_dest.joinpath(filename))

    @staticmethod
    def _write_json_file(data: Union[dict, list], out_file: Path):
        json_data = json.dumps(data, indent=4, default=str)

        with open(out_file, "w") as f:
            f.write(json_data)

    def finish_export(self):
        zip_path = app_dirs.BACKUP_DIR.joinpath(f"{self.main_dir.name}")
        shutil.make_archive(zip_path, "zip", self.main_dir)

        shutil.rmtree(app_dirs.TEMP_DIR)

        return str(zip_path.absolute()) + ".zip"


def backup_all(
    session,
    tag=None,
    templates=None,
    export_recipes=True,
    export_settings=True,
    export_pages=True,
    export_themes=True,
    export_users=True,
    export_groups=True,
):
    db_export = ExportDatabase(tag=tag, templates=templates)

    if export_users:
        all_users = db.users.get_all(session)
        db_export.export_items(all_users, "users")

    if export_groups:
        all_groups = db.groups.get_all(session)
        db_export.export_items(all_groups, "groups")

    if export_recipes:
        all_recipes = db.recipes.get_all(session)
        db_export.export_recipe_dirs()
        db_export.export_items(all_recipes, "recipes", export_list=False, slug_folder=True)
        db_export.export_templates(all_recipes)

    if export_settings:
        all_settings = db.settings.get_all(session)
        db_export.export_items(all_settings, "settings")

    if export_pages:
        all_pages = db.custom_pages.get_all(session)
        db_export.export_items(all_pages, "pages")

    if export_themes:
        all_themes = db.themes.get_all(session)
        db_export.export_items(all_themes, "themes")

    return db_export.finish_export()


def auto_backup_job():
    for backup in app_dirs.BACKUP_DIR.glob("Auto*.zip"):
        backup.unlink()

    templates = [template for template in app_dirs.TEMPLATE_DIR.iterdir()]
    session = create_session()
    backup_all(session=session, tag="Auto", templates=templates)
    logger.info("Auto Backup Called")
