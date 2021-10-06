import tempfile
import zipfile
from pathlib import Path

from mealie.core.config import get_app_dirs

app_dirs = get_app_dirs()


def unpack_zip(selection: Path) -> tempfile.TemporaryDirectory:
    app_dirs.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory(dir=app_dirs.TEMP_DIR)
    temp_dir_path = Path(temp_dir.name)
    if selection.suffix == ".zip":
        with zipfile.ZipFile(selection, "r") as zip_ref:
            zip_ref.extractall(path=temp_dir_path)

    else:
        raise Exception("File is not a zip file")

    return temp_dir
