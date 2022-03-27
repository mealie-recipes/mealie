import os
from pathlib import Path

megabyte = 1_048_576
gigabyte = 1_073_741_824


def pretty_size(size: int) -> str:
    """
    Pretty size takes in a integer value of a file size and returns the most applicable
    file unit and the size.
    """
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 ** 2:
        return f"{round(size / 1024, 2)} KB"
    elif size < 1024 ** 2 * 1024:
        return f"{round(size / 1024 / 1024, 2)} MB"
    elif size < 1024 ** 2 * 1024 * 1024:
        return f"{round(size / 1024 / 1024 / 1024, 2)} GB"
    else:
        return f"{round(size / 1024 / 1024 / 1024 / 1024, 2)} TB"


def get_dir_size(path: Path | str) -> int:
    """
    Get the size of a directory
    """
    try:
        total_size = os.path.getsize(path)
    except FileNotFoundError:
        return 0

    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_dir_size(itempath)
    return total_size
