import tempfile
import zipfile
from pathlib import Path

from app_config import TEMP_DIR


def unpack_zip(selection: Path) -> tempfile.TemporaryDirectory:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory(dir=TEMP_DIR)
    temp_dir_path = Path(temp_dir.name)
    if selection.suffix == ".zip":
        with zipfile.ZipFile(selection, "r") as zip_ref:
            zip_ref.extractall(path=temp_dir_path)

    else:
        raise Exception("File is not a zip file")

    return temp_dir
