import shutil
from pathlib import Path

from mealie.assets import templates


class AppDirectories:
    def __init__(self, data_dir: Path) -> None:
        self.DATA_DIR = data_dir
        self.BACKUP_DIR = data_dir.joinpath("backups")
        self.USER_DIR = data_dir.joinpath("users")
        self.RECIPE_DATA_DIR = data_dir.joinpath("recipes")
        self.TEMPLATE_DIR = data_dir.joinpath("templates")

        self.GROUPS_DIR = self.DATA_DIR.joinpath("groups")

        # Deprecated
        self._TEMP_DIR = data_dir.joinpath(".temp")
        self._IMG_DIR = data_dir.joinpath("img")
        self.ensure_directories()

    @property
    def IMG_DIR(self):
        return self._IMG_DIR

    @property
    def TEMP_DIR(self):
        return self._TEMP_DIR

    def ensure_directories(self):
        required_dirs = [
            self.GROUPS_DIR,
            self.BACKUP_DIR,
            self.TEMPLATE_DIR,
            self.RECIPE_DATA_DIR,
            self.USER_DIR,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)

        # Boostrap Templates
        markdown_template = self.TEMPLATE_DIR.joinpath("recipes.md")

        if not markdown_template.exists():
            shutil.copyfile(templates.recipes_markdown, markdown_template)
