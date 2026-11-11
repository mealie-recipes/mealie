import gzip
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest

from mealie.pkgs.archive import ArchiveBudget, ArchiveTooLargeError


def _zip(files: dict[str, bytes]) -> ZipFile:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zip_file:
        for name, content in files.items():
            zip_file.writestr(name, content)
    return ZipFile(buffer)


def _budget(bytes_left: int = 1000, entries_left: int = 10, max_file_size: int = 1000) -> ArchiveBudget:
    return ArchiveBudget(bytes_left=bytes_left, entries_left=entries_left, max_file_size=max_file_size)


def test_spend_charges_bytes_and_entries():
    budget = _budget(bytes_left=10, entries_left=3)

    assert budget.spend(_zip({"one.txt": b"12345", "two.txt": b"678"})) == 8

    assert budget.bytes_left == 2
    assert budget.entries_left == 1


def test_spend_rejects_total_over_budget():
    with pytest.raises(ArchiveTooLargeError):
        _budget(bytes_left=7).spend(_zip({"one.txt": b"12345", "two.txt": b"678"}))


def test_spend_rejects_too_many_entries():
    with pytest.raises(ArchiveTooLargeError):
        _budget(entries_left=2).spend(_zip({"a": b"", "b": b"", "c": b""}))


def test_spend_rejects_one_file_over_file_limit():
    with pytest.raises(ArchiveTooLargeError):
        _budget(max_file_size=4).spend(_zip({"big.json": b"12345"}))


def test_spend_allows_nested_zip_over_file_limit():
    budget = _budget(max_file_size=4)

    assert budget.spend(_zip({"cookbook.zip": b"12345"})) == 5


def test_budget_is_shared_across_archives():
    budget = _budget(bytes_left=8)
    budget.spend(_zip({"one.txt": b"12345"}))

    with pytest.raises(ArchiveTooLargeError):
        budget.spend(_zip({"two.txt": b"6789"}))


def test_read_gzip_at_limit(tmp_path: Path):
    path = tmp_path / "a.gz"
    path.write_bytes(gzip.compress(b"0" * 100))
    budget = _budget(max_file_size=100)

    assert budget.read_gzip(path) == b"0" * 100
    assert budget.bytes_left == 900


@pytest.mark.parametrize("budget", [_budget(max_file_size=99), _budget(bytes_left=99)])
def test_read_gzip_over_limit(tmp_path: Path, budget: ArchiveBudget):
    path = tmp_path / "a.gz"
    path.write_bytes(gzip.compress(b"0" * 100))

    with pytest.raises(ArchiveTooLargeError):
        budget.read_gzip(path)
