import pytest

from mealie.utils.fs_stats import pretty_size


@pytest.mark.parametrize(
    "size, expected",
    [
        (0, "0 bytes"),
        (1, "1 bytes"),
        (1024, "1.0 KB"),
        (1024 ** 2, "1.0 MB"),
        (1024 ** 2 * 1024, "1.0 GB"),
        (1024 ** 2 * 1024 * 1024, "1.0 TB"),
    ],
)
def test_pretty_size(size: int, expected: str) -> None:
    """
    Test pretty size takes in a integer value of a file size and returns the most applicable
    file unit and the size.
    """
    assert pretty_size(size) == expected
