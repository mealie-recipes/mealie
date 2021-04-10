def split_by_comma(tag_string: str):
    """Splits a single string by ',' performs a line strip and then title cases the resulting string

    Args:
        tag_string (str): [description]

    Returns:
        [type]: [description]
    """
    if not isinstance(tag_string, str):
        return None
    return [x.title().lstrip() for x in tag_string.split(",") if x != ""]
