from pathlib import Path

from mealie.core import security
from mealie.core.dependencies import validate_file_token


def test_create_file_token():
    file_path = Path(__file__).parent
    file_token = security.create_file_token(file_path)

    assert file_path == validate_file_token(file_token)
