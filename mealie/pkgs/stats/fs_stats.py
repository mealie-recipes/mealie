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
