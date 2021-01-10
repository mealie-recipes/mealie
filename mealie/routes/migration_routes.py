from fastapi import APIRouter, HTTPException
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
