import json
import shutil
import tempfile
from pathlib import Path


class BackupContents:
    _tables: dict | None = None

    def __init__(self, file: Path) -> None:
        self.base = self._find_base(file)
        self.data_directory = self._find_data_dir_from_base(self.base)
        self.tables = self._find_database_from_base(self.base)

    @classmethod
    def _find_base(cls, file: Path) -> Path:
        # Safari mangles our ZIP structure and adds a "__MACOSX" directory at the root along with
        # an arbitrarily-named directory containing the actual contents. So, if we find a dunder directory
        # at the root (i.e. __MACOSX) we traverse down the first non-dunder directory and assume this is the base.
        # This works because our backups never contain a directory that starts with "__".
        dirs = [d for d in file.iterdir() if d.is_dir()]
        dunder_dirs = [d for d in dirs if d.name.startswith("__")]
        normal_dirs = [d for d in dirs if not d.name.startswith("__")]

        if not dunder_dirs:
            return file

        # If the backup somehow adds a __MACOSX directory alongside the data directory, rather than in the
        # parent directory, we don't want to traverse down. We check for our database.json file, and if it exists,
        # we're already at the correct base.
        if cls._find_database_from_base(file).exists():
            return file

        # This ZIP file was mangled, so we return the first non-dunder directory (if it exists).
        return normal_dirs[0] if normal_dirs else file

    @classmethod
    def _find_data_dir_from_base(cls, base: Path) -> Path:
        return base / "data"

    @classmethod
    def _find_database_from_base(cls, base: Path) -> Path:
        return base / "database.json"

    def validate(self) -> bool:
        if not self.base.is_dir():
            return False

        if not self.data_directory.is_dir():
            return False

        if not self.tables.is_file():
            return False

        return True

    def schema_version(self) -> str:
        tables = self.read_tables()

        alembic_version = tables.get("alembic_version", [])

        if not alembic_version:
            return ""

        return alembic_version[0].get("version_num", "")

    def read_tables(self) -> dict:
        if self._tables is None:
            with open(self.tables) as f:
                self._tables = json.load(f)

        return self._tables


class BackupFile:
    temp_dir: Path | None = None

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
