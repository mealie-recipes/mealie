from pathlib import Path

import pytest
from pytest import MonkeyPatch

from mealie.core.settings.directories import AppDirectories
from mealie.services.backups_v2.backup_v2 import BackupV2


@pytest.mark.parametrize("destination_exists", [False, True])
def test_copy_data_restores_missing_and_existing_directories(
    tmp_path: Path, monkeypatch: MonkeyPatch, destination_exists: bool
) -> None:
    backup = BackupV2()
    monkeypatch.setattr(backup, "directories", AppDirectories(tmp_path / "current-data"))
    source = tmp_path / "backup-data" / "repro-new"
    source.mkdir(parents=True)
    (source / "restored.txt").write_text("backup contents")
    nested = source / "nested"
    nested.mkdir()
    (nested / "attachment.txt").write_text("nested contents")

    destination = backup.directories.DATA_DIR / source.name
    if destination_exists:
        destination.mkdir()
        (destination / "stale.txt").write_text("not in the backup")

    try:
        backup._copy_data(source.parent)

        assert (destination / "restored.txt").read_text() == "backup contents"
        assert (destination / "nested" / "attachment.txt").read_text() == "nested contents"
        assert not (destination / "stale.txt").exists()
    finally:
        backup.db_exporter.engine.dispose()


def test_copy_data_propagates_directory_removal_errors(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    backup = BackupV2()
    monkeypatch.setattr(backup, "directories", AppDirectories(tmp_path / "current-data"))
    source = tmp_path / "backup-data" / "repro-new"
    source.mkdir(parents=True)
    destination = backup.directories.DATA_DIR / source.name
    destination.mkdir()
    original = destination / "original.txt"
    original.write_text("existing contents")

    def fail_removal(path: Path) -> None:
        raise PermissionError("destination cannot be removed")

    with monkeypatch.context() as patch:
        patch.setattr("mealie.services.backups_v2.backup_v2.shutil.rmtree", fail_removal)
        try:
            with pytest.raises(PermissionError, match="destination cannot be removed"):
                backup._copy_data(source.parent)
        finally:
            backup.db_exporter.engine.dispose()

    assert original.read_text() == "existing contents"
