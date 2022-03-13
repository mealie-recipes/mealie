import json
import shutil
import tempfile
from pathlib import Path


class BackupContents:
    def __init__(self, file: Path) -> None:
        self.base = file
        self.data_directory = self.base / "data"
        self.tables = self.base / "database.json"

    def validate(self) -> bool:
        if not self.base.is_dir():
            return False

        if not self.data_directory.is_dir():
            return False

        if not self.tables.is_file():
            return False

        return True

    def read_tables(self) -> dict:
        with open(self.tables) as f:
            return json.loads(f.read())


class BackupFile:
    temp_dir: Path | None

    def __init__(self, file: Path) -> None:
        self.zip = file

    def __enter__(self) -> BackupContents:
        self.temp_dir = Path(tempfile.mkdtemp())
        shutil.unpack_archive(str(self.zip), str(self.temp_dir))
        return BackupContents(self.temp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and self.temp_dir.is_dir():
            shutil.rmtree(self.temp_dir)

            self.temp_dir = None
