import filecmp
from pathlib import Path
from pprint import pprint

from mealie.core.config import get_app_settings
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.backups_v2.backup_file import BackupFile
from mealie.services.backups_v2.backup_v2 import BackupV2


# For Future Use
def match_file_tree(path_a: Path, path_b: Path):
    if path_a.is_dir() and path_b.is_dir():
        for a_file in path_a.iterdir():
            b_file = path_b.joinpath(a_file.name)
            assert b_file.exists()
            match_file_tree(a_file, b_file)
    else:
        assert filecmp(path_a, path_b)


def test_database_backup():
    backup_v2 = BackupV2()
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()

    backup = BackupFile(path_to_backup)

    with backup as contents:
        assert contents.validate()


def test_database_restore():
    settings = get_app_settings()

    # Capture existing database snapshot
    original_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_1 = original_exporter.dump()

    # Create Backup
    backup_v2 = BackupV2(settings.DB_URL)
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()
    backup_v2.restore(path_to_backup)

    new_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_2 = new_exporter.dump()

    # print("--- Original ---")
    # pprint(snapshop_1)
    # print("--- New ---")
    # pprint(snapshop_2)
    assert snapshop_1 == snapshop_2
