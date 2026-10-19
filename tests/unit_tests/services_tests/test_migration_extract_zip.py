from pathlib import Path
from zipfile import ZipFile

import pytest

from mealie.services.migrations.utils.migration_helpers import ArchiveTooLargeError, extract_zip


def _make_zip(path: Path, files: dict[str, bytes]) -> Path:
    with ZipFile(path, "w") as zip_file:
        for name, content in files.items():
            zip_file.writestr(name, content)
    return path


def test_extract_zip_returns_bytes_written(tmp_path: Path):
    archive = _make_zip(tmp_path / "a.zip", {"one.txt": b"12345", "dir/two.txt": b"678"})
    dest = tmp_path / "out"

    assert extract_zip(archive, dest, max_size=8) == 8
    assert (dest / "dir" / "two.txt").read_bytes() == b"678"


def test_extract_zip_over_limit_writes_nothing(tmp_path: Path):
    archive = _make_zip(tmp_path / "a.zip", {"one.txt": b"0" * 100})
    dest = tmp_path / "out"

    with pytest.raises(ArchiveTooLargeError):
        extract_zip(archive, dest, max_size=99)

    assert not dest.exists()
