import pytest
from unittest.mock import patch
from pathlib import Path
from mealie.pkgs.stats.fs_stats import pretty_size, get_dir_size


def test_pretty_size_bytes():
    assert pretty_size(500) == "500 bytes"

def test_pretty_size_kilobytes():
    assert pretty_size(2048) == "2.0 KB"

def test_pretty_size_megabytes():
    assert pretty_size(1048576 * 5) == "5.0 MB"

def test_pretty_size_gigabytes():
    assert pretty_size(1073741824 * 2) == "2.0 GB"

def test_pretty_size_terabytes():
    assert pretty_size(1099511627776) == "1.0 TB"



def test_get_dir_size_file_not_found():
    with patch("os.path.getsize", side_effect=FileNotFoundError):
        assert get_dir_size("non_existent_folder") == 0

def test_get_dir_size_with_files(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("12345") 
    
    size = get_dir_size(d)
    assert size >= 5

def test_get_dir_size_with_nested_subdirectory(tmp_path):
    parent = tmp_path / "parent"
    child = parent / "child"
    child.mkdir(parents=True)
    
    file_in_child = child / "test.txt"
    file_in_child.write_text("12345") 
    
    size = get_dir_size(parent)
    assert size >= 5
