import json
import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Template
from services.recipe_services import Recipe
from services.settings_services import SiteSettings, SiteTheme
from settings import BACKUP_DIR, IMG_DIR, TEMP_DIR, TEMPLATE_DIR
from utils.logger import logger


class ExportDatabase:
    def __init__(self, tag=None, templates=None) -> None:
        """Export a Mealie database. Export interacts directly with class objects and can be used
        with any supported backend database platform. By default tags are timestands, and no Jinja2 templates are rendered


        Args:
            tag ([str], optional): A str to be used as a file tag. Defaults to None.
            templates (list, optional): A list of template file names. Defaults to None.
        """
        if tag:
            export_tag = tag + "_" + datetime.now().strftime("%Y-%b-%d")
        else:
            export_tag = datetime.now().strftime("%Y-%b-%d")

        self.main_dir = TEMP_DIR.joinpath(export_tag)
        self.img_dir = self.main_dir.joinpath("images")
        self.recipe_dir = self.main_dir.joinpath("recipes")
        self.themes_dir = self.main_dir.joinpath("themes")
        self.settings_dir = self.main_dir.joinpath("settings")
        self.templates_dir = self.main_dir.joinpath("templates")
        self.mealplans_dir = self.main_dir.joinpath("mealplans")

        try:
            self.templates = [TEMPLATE_DIR.joinpath(x) for x in templates]
        except:
            self.templates = False
            logger.info("No Jinja2 Templates Registered for Export")

        required_dirs = [
            self.main_dir,
            self.img_dir,
            self.recipe_dir,
            self.themes_dir,
            self.settings_dir,
            self.templates_dir,
            self.mealplans_dir,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)

    def export_recipes(self):
        all_recipes = Recipe.get_all()

        for recipe in all_recipes:
            logger.info(f"Backing Up Recipes: {recipe}")

            filename = recipe.get("slug") + ".json"
            file_path = self.recipe_dir.joinpath(filename)

            ExportDatabase._write_json_file(recipe, file_path)

            if self.templates:
                self._export_template(recipe)

    def _export_template(self, recipe_data: dict):
        for template_path in self.templates:

            with open(template_path, "r") as f:
                template = Template(f.read())

            filename = recipe_data.get("name") + template_path.suffix
            out_file = self.templates_dir.joinpath(filename)

            content = template.render(recipe=recipe_data)

            with open(out_file, "w") as f:
                f.write(content)

    def export_images(self):
        for file in IMG_DIR.iterdir():
            shutil.copy(file, self.img_dir.joinpath(file.name))

    def export_settings(self):
        all_settings = SiteSettings.get_site_settings()
        out_file = self.settings_dir.joinpath("settings.json")
        ExportDatabase._write_json_file(all_settings.dict(), out_file)

    def export_themes(self):
        all_themes = SiteTheme.get_all()
        print(all_themes)
        if all_themes:
            all_themes = [x.dict() for x in all_themes]
            out_file = self.themes_dir.joinpath("themes.json")
            ExportDatabase._write_json_file(all_themes, out_file)

    # def export_meals(self): #! Problem Parseing Datetime Objects... May come back to this
    #     meal_plans = MealPlan.get_all()
    #     if meal_plans:
    #         meal_plans = [x.dict() for x in meal_plans]

    #     print(meal_plans)
    #     out_file = self.mealplans_dir.joinpath("mealplans.json")
    #     DatabaseExport._write_json_file(meal_plans, out_file)

    @staticmethod
    def _write_json_file(data, out_file: Path):
        json_data = json.dumps(data, indent=4)

        with open(out_file, "w") as f:
            f.write(json_data)

    def finish_export(self):
        zip_path = BACKUP_DIR.joinpath(f"{self.main_dir.name}")
        shutil.make_archive(zip_path, "zip", self.main_dir)

        shutil.rmtree(TEMP_DIR)

        return str(zip_path.absolute()) + ".zip"


def backup_all(tag=None, templates=None):
    db_export = ExportDatabase(tag=tag, templates=templates)

    db_export.export_recipes()
    db_export.export_images()
    db_export.export_settings()
    db_export.export_themes()
    # db_export.export_meals()

    return db_export.finish_export()


def auto_backup_job():
    for backup in BACKUP_DIR.glob("Auto*.zip"):
        backup.unlink()

    templates = []
    for template in TEMPLATE_DIR.iterdir():
        templates.append(template)

    backup_all(tag="Auto", templates=templates)
    logger.info("Auto Backup Called")
