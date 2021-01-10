import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from models.migration_models import ChowdownURL
from services.migrations.chowdown import chowdown_migrate as chowdow_migrate
from services.migrations.nextcloud import migrate as nextcloud_migrate
from settings import MIGRATION_DIR
from utils.snackbar import SnackResponse

router = APIRouter()


# Chowdown
@router.post("/api/migration/chowdown/repo/", tags=["Migration"])
async def import_chowdown_recipes(repo: ChowdownURL):
    """ Import Chowsdown Recipes from Repo URL """
    try:
        report = chowdow_migrate(repo.url)
        return SnackResponse.success(
            "Recipes Imported from Git Repo, see report for failures.",
            additional_data=report,
        )
    except:
        return HTTPException(
            status_code=400,
            detail=SnackResponse.error(
                "Unable to Migrate Recipes. See Log for Details"
            ),
        )


# Nextcloud
@router.get("/api/migration/nextcloud/available/", tags=["Migration"])
async def get_avaiable_nextcloud_imports():
    """ Returns a list of avaiable directories that can be imported into Mealie """
    available = []
    for dir in MIGRATION_DIR.iterdir():
        if dir.is_dir():
            available.append(dir.stem)
        elif dir.suffix == ".zip":
            available.append(dir.name)

    return available


@router.post("/api/migration/nextcloud/{selection}/import/", tags=["Migration"])
async def import_nextcloud_directory(selection: str):
    """ Imports all the recipes in a given directory """

    return nextcloud_migrate(selection)


@router.delete("/api/migration/{file_folder_name}/delete/", tags=["Migration"])
async def delete_migration_data(file_folder_name: str):
    """ Removes migration data from the file system """

    remove_path = MIGRATION_DIR.joinpath(file_folder_name)

    if remove_path.is_file():
        remove_path.unlink()
    elif remove_path.is_dir():
        shutil.rmtree(remove_path)
    else:
        SnackResponse.error("File/Folder not found.")

    return SnackResponse.info(f"Migration Data Remove: {remove_path.absolute()}")


@router.post("/api/migration/upload/", tags=["Migration"])
async def upload_nextcloud_zipfile(archive: UploadFile = File(...)):
    """ Upload a .zip File to later be imported into Mealie """
    dest = MIGRATION_DIR.joinpath(archive.filename)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    if dest.is_file:
        return SnackResponse.success("Migration data uploaded")
    else:
        return SnackResponse.error("Failure uploading file")
