import datetime
import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.services._base_service import BaseService
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.backups_v2.backup_file import BackupFile


class BackupSchemaMismatch(Exception): ...


@dataclass
class BackupResult:
    path: Path
    duplicate: bool = False
    duplicateOf: str | None = None


class BackupV2(BaseService):
    EXCLUDE_DIRS = {"backups", ".temp"}
    EXCLUDE_FILES = {"mealie.db"}
    EXCLUDE_FILES_REGEX = {re.compile(r"^mealie\.log(?:\.\d+)?$")}
    EXCLUDE_EXTENTIONS = {".zip"}

    RESTORE_FILES = {".secret"}

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

    def _hash_zip(self, zip_path: Path) -> str:
        h = hashlib.md5()
        with zip_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _find_duplicate(self, hash: str) -> Path | None:
        for zip_path in self.directories.BACKUP_DIR.glob("*.zip"):
            sidecar = zip_path.with_suffix(".zip.md5")
            if sidecar.is_file() and sidecar.read_text().strip() == hash:
                return zip_path
        return None

    def backup(self) -> BackupResult:
        # sourcery skip: merge-nested-ifs, reintroduce-else, remove-redundant-continue
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y.%m.%d.%H.%M.%S")
        short_hash = self.settings.GIT_COMMIT_HASH[:7]

        if APP_VERSION == "develop":
            backup_name = f"mealie_dev-{short_hash}_{timestamp}.zip"
        elif APP_VERSION == "nightly":
            backup_name = f"mealie_nightly-{short_hash}_{timestamp}.zip"
        else:
            backup_name = f"mealie_{APP_VERSION}_{timestamp}.zip"

        backup_file = self.directories.BACKUP_DIR / backup_name

        temp_file = self.directories.BACKUP_DIR / f".temp_{backup_name}"

        try:
            database_json = self.db_exporter.dump()
            database_str = json.dumps(database_json, sort_keys=True)

            with ZipFile(temp_file, "w", compression=ZIP_DEFLATED) as zip_file:
                epoch_time = (1980, 1, 1, 0, 0, 0)

                db_info = ZipInfo("database.json")
                db_info.date_time = epoch_time
                db_info.compress_type = ZIP_DEFLATED
                zip_file.writestr(db_info, database_str)

                for data_file in sorted(self.directories.DATA_DIR.glob("**/*")):
                    if data_file.name in self.EXCLUDE_FILES:
                        continue
                    if any(pattern.search(data_file.name) for pattern in self.EXCLUDE_FILES_REGEX):
                        continue
                    if data_file.is_file() and data_file.suffix not in self.EXCLUDE_EXTENTIONS:
                        if data_file.parent.name in self.EXCLUDE_DIRS:
                            continue
                        archive_path = f"data/{data_file.relative_to(self.directories.DATA_DIR)}"
                        file_info = ZipInfo(archive_path)
                        file_info.date_time = epoch_time
                        file_info.compress_type = ZIP_DEFLATED
                        zip_file.writestr(file_info, data_file.read_bytes())

            new_hash = self._hash_zip(temp_file)
            duplicate = self._find_duplicate(new_hash)

            backup_file = self.directories.BACKUP_DIR / backup_name
            backup_file.with_suffix(".zip.md5").write_text(new_hash)

            if duplicate:
                os.link(duplicate, backup_file)
                temp_file.unlink()
                return BackupResult(path=backup_file, duplicate=True, duplicateOf=duplicate.name)

            temp_file.rename(backup_file)
            return BackupResult(path=backup_file, duplicate=False)

        except Exception:
            if temp_file.is_file():
                temp_file.unlink()
            raise

    def _copy_data(self, data_path: Path) -> None:
        for f in data_path.iterdir():
            if f.is_file():
                if f.name not in self.RESTORE_FILES:
                    continue

                shutil.copyfile(f, self.directories.DATA_DIR / f.name)
                continue

            shutil.rmtree(self.directories.DATA_DIR / f.name)
            shutil.copytree(f, self.directories.DATA_DIR / f.name)

        # since we copied a new .secret, AppSettings has the wrong secret info
        self.logger.info("invalidating appsettings cache")
        get_app_settings.cache_clear()
        self.settings = get_app_settings()

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
