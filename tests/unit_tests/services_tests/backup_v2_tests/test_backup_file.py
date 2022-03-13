import json
from pathlib import Path
from zipfile import ZipFile

from mealie.services.backups_v2.backup_file import BackupFile
from tests import utils


def zip_factory(temp_dir) -> Path:
    temp_zip = temp_dir / f"{utils.random_string()}.zip"

    with ZipFile(temp_zip, "w") as zip_file:
        zip_file.writestr("test.txt", "test")

    return temp_zip


def test_backup_file_context_manager(tmp_path: Path):
    temp_zip = zip_factory(tmp_path)

    backup_file = BackupFile(temp_zip)

    with backup_file as _:
        assert backup_file.temp_dir.exists()
        temp_dir_path = backup_file.temp_dir

    assert not backup_file.temp_dir
    assert not temp_dir_path.exists()


def test_backup_file_invalid_zip(tmp_path: Path):
    temp_zip = zip_factory(tmp_path)

    backup_file = BackupFile(temp_zip)

    with backup_file as content:
        assert not content.validate()


def test_backup_file_valid_zip(tmp_path: Path):
    dummy_dict = {"hello": "world"}

    temp_zip = zip_factory(tmp_path)

    # Add contents
    with ZipFile(temp_zip, "a") as zip_file:
        zip_file.writestr("data/test.txt", "test")
        zip_file.writestr("database.json", json.dumps(dummy_dict))

    backup_file = BackupFile(temp_zip)

    with backup_file as content:
        assert content.validate()

        assert content.read_tables() == dummy_dict
        assert content.data_directory.joinpath("test.txt").is_file()
