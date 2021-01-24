import operator
import shutil
from typing import List

from app_config import MIGRATION_DIR
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from models.migration_models import MigrationFile, Migrations
from services.migrations.chowdown import chowdown_migrate as chowdow_migrate
from services.migrations.nextcloud import migrate as nextcloud_migrate
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(tags=["Migration"])


@router.get("/api/migrations/", response_model=List[Migrations])
def get_avaiable_nextcloud_imports():
    """ Returns a list of avaiable directories that can be imported into Mealie """
    response_data = []
    migration_dirs = [
        MIGRATION_DIR.joinpath("nextcloud"),
        MIGRATION_DIR.joinpath("chowdown"),
    ]
    for directory in migration_dirs:
        migration = Migrations(type=directory.stem)
        for zip in directory.iterdir():
            if zip.suffix == ".zip":
                migration_zip = MigrationFile(name=zip.name, date=zip.stat().st_ctime)
                migration.files.append(migration_zip)
        response_data.append(migration)

        migration.files.sort(key=operator.attrgetter("date"), reverse=True)

    return response_data


@router.post("/api/migrations/{type}/{file_name}/import/")
def import_nextcloud_directory(
    type: str, file_name: str, db: Session = Depends(generate_session)
):
    """ Imports all the recipes in a given directory """
    file_path = MIGRATION_DIR.joinpath(type, file_name)
    if type == "nextcloud":
        return nextcloud_migrate(db, file_path)
    elif type == "chowdown":
        return chowdow_migrate(db, file_path)
    else:
        return SnackResponse.error("Incorrect Migration Type Selected")


@router.delete("/api/migrations/{folder}/{file}/delete/")
def delete_migration_data(folder: str, file: str):
    """ Removes migration data from the file system """

    remove_path = MIGRATION_DIR.joinpath(folder, file)

    if remove_path.is_file():
        remove_path.unlink()
    elif remove_path.is_dir():
        shutil.rmtree(remove_path)
    else:
        SnackResponse.error("File/Folder not found.")

    return SnackResponse.info(f"Migration Data Remove: {remove_path.absolute()}")


@router.post("/api/migrations/{type}/upload/")
def upload_nextcloud_zipfile(type: str, archive: UploadFile = File(...)):
    """ Upload a .zip File to later be imported into Mealie """
    dir = MIGRATION_DIR.joinpath(type)
    dir.mkdir(parents=True, exist_ok=True)
    dest = dir.joinpath(archive.filename)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    if dest.is_file:
        return SnackResponse.success("Migration data uploaded")
    else:
        return SnackResponse.error("Failure uploading file")
