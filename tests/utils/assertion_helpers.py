def assert_ignore_keys(dict1: dict, dict2: dict, ignore_keys: list) -> None:
    """
    Itterates through a list of keys and checks if they are in the the provided ignore_keys list,
    if they are not in the ignore_keys list, it checks the value of the key in the provided against
    the value provided in dict2. If the value of the key in dict1 is not equal to the value of the
    key in dict2, The assertion fails. Useful for testing id / group_id agnostic data

    Note: ignore_keys defaults to ['id', 'group_id']
    """
    if ignore_keys is None:
        ignore_keys = ["id", "group_id"]

    for key, value in dict1.items():
        if key in ignore_keys:
            continue
        else:
            assert value == dict2[key]
