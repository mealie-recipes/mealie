from pathlib import Path


class AppDirectories:
    def __init__(self, data_dir) -> None:
        self.DATA_DIR: Path = data_dir
        self.IMG_DIR: Path = data_dir.joinpath("img")
        self.BACKUP_DIR: Path = data_dir.joinpath("backups")
        self.DEBUG_DIR: Path = data_dir.joinpath("debug")
        self.MIGRATION_DIR: Path = data_dir.joinpath("migration")
        self.NEXTCLOUD_DIR: Path = self.MIGRATION_DIR.joinpath("nextcloud")
        self.CHOWDOWN_DIR: Path = self.MIGRATION_DIR.joinpath("chowdown")
        self.TEMPLATE_DIR: Path = data_dir.joinpath("templates")
        self.USER_DIR: Path = data_dir.joinpath("users")
        self.RECIPE_DATA_DIR: Path = data_dir.joinpath("recipes")
        self.TEMP_DIR: Path = data_dir.joinpath(".temp")

        self.ensure_directories()

    def ensure_directories(self):
        required_dirs = [
            self.IMG_DIR,
            self.BACKUP_DIR,
            self.DEBUG_DIR,
            self.MIGRATION_DIR,
            self.TEMPLATE_DIR,
            self.NEXTCLOUD_DIR,
            self.CHOWDOWN_DIR,
            self.RECIPE_DATA_DIR,
            self.USER_DIR,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)
