from pathlib import Path
from zipfile import ZipFile

import pytest

from mealie.pkgs.archive import ArchiveBudget, ArchiveTooLargeError
from mealie.services.migrations.utils.migration_helpers import extract_zip


def _make_zip(path: Path, files: dict[str, bytes]) -> Path:
    with ZipFile(path, "w") as zip_file:
        for name, content in files.items():
            zip_file.writestr(name, content)
    return path


def test_extract_zip_charges_budget(tmp_path: Path):
    archive = _make_zip(tmp_path / "a.zip", {"one.txt": b"12345", "dir/two.txt": b"678"})
    dest = tmp_path / "out"
    budget = ArchiveBudget(bytes_left=8, entries_left=2, max_file_size=8)

    extract_zip(archive, dest, budget)

    assert (dest / "dir" / "two.txt").read_bytes() == b"678"
    assert budget.bytes_left == 0


def test_extract_zip_over_limit_writes_nothing(tmp_path: Path):
    archive = _make_zip(tmp_path / "a.zip", {"one.txt": b"0" * 100})
    dest = tmp_path / "out"

    with pytest.raises(ArchiveTooLargeError):
        extract_zip(archive, dest, ArchiveBudget(bytes_left=99, entries_left=1, max_file_size=100))

    assert not dest.exists()
