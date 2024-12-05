import datetime
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

from mealie.services._base_service import BaseService
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.backups_v2.backup_file import BackupFile


class BackupSchemaMismatch(Exception): ...


class BackupV2(BaseService):
    def __init__(self, db_url: str | None = None) -> None:
        super().__init__()

        # type - one of these has to be a string
        self.db_url: str = db_url or self.settings.DB_URL  # type: ignore

        self.db_exporter = AlchemyExporter(self.db_url)

    def _sqlite(self) -> None:
        db_file = self.settings.DB_URL.removeprefix("sqlite:///")  # type: ignore

        # Create a backup of the SQLite database
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y.%m.%d")
        shutil.copy(db_file, self.directories.DATA_DIR.joinpath(f"mealie_{timestamp}.bak.db"))

    def _postgres(self) -> None:
        pass

    def backup(self) -> Path:
        # sourcery skip: merge-nested-ifs, reintroduce-else, remove-redundant-continue
        exclude = {"mealie.db", "mealie.log", ".secret"}
        exclude_ext = {".zip"}
        exclude_dirs = {"backups", ".temp"}

        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y.%m.%d.%H.%M.%S")

        backup_name = f"mealie_{timestamp}.zip"
        backup_file = self.directories.BACKUP_DIR / backup_name

        database_json = self.db_exporter.dump()

        with ZipFile(backup_file, "w") as zip_file:
            zip_file.writestr("database.json", json.dumps(database_json))

            for data_file in self.directories.DATA_DIR.glob("**/*"):
                if data_file.name in exclude:
                    continue

                if data_file.is_file() and data_file.suffix not in exclude_ext:
                    if data_file.parent.name in exclude_dirs:
                        continue

                    zip_file.write(data_file, f"data/{data_file.relative_to(self.directories.DATA_DIR)}")

        return backup_file

    def _copy_data(self, data_path: Path) -> None:
        for f in data_path.iterdir():
            if f.is_file():
                continue

            shutil.rmtree(self.directories.DATA_DIR / f.name)
            shutil.copytree(f, self.directories.DATA_DIR / f.name)

    def restore(self, backup_path: Path) -> None:
        self.logger.info("initializing backup restore")

        backup = BackupFile(backup_path)

        if self.settings.DB_ENGINE == "sqlite":
            self._sqlite()
        elif self.settings.DB_ENGINE == "postgres":
            self._postgres()

        with backup as contents:
            # ================================
            # Validation
            if not contents.validate():
                self.logger.error(
                    "Invalid backup file. file does not contain required elements (data directory and database.json)"
                )
                raise ValueError("Invalid backup file")

            database_json = contents.read_tables()

            # ================================
            # Purge Database

            self.logger.info("dropping all database tables")
            self.db_exporter.drop_all()

            # ================================
            # Restore Database

            self.logger.info("importing database tables")
            self.db_exporter.restore(database_json)

            self.logger.info("database tables imported successfully")

            self.logger.info("restoring data directory")
            self._copy_data(contents.data_directory)
            self.logger.info("data directory restored successfully")

        self.logger.info("backup restore complete")
