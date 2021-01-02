from fastapi import APIRouter, HTTPException
from models.backup_models import BackupJob
from services.migrations.chowdown import chowdown_migrate as chowdow_migrate
from utils.snackbar import SnackResponse

router = APIRouter()


@router.post("/api/migration/chowdown/repo/", tags=["Migration"])
async def import_chowdown_recipes(repo: dict):
    """ Import Chowsdown Recipes from Repo URL """
    try:
        report = chowdow_migrate(repo.get("url"))
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
