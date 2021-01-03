from fastapi import APIRouter, HTTPException
from models.backup_models import BackupJob
from services.backup_services import (BACKUP_DIR, TEMPLATE_DIR, export_db,
                                      import_from_archive)
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/backups/available/", tags=["Import / Export"])
async def available_imports():
    """ Returns this weeks meal plan """
    imports = []
    templates = []
    for archive in BACKUP_DIR.glob("*.zip"):
        imports.append(archive.name)

    for template in TEMPLATE_DIR.glob("*.md"):
        templates.append(template.name)

    return {"imports": imports, "templates": templates}


@router.post("/api/backups/export/database/", tags=["Import / Export"], status_code=201)
async def export_database(data: BackupJob):
    """ Returns this weeks meal plan """

    try:
        export_db(data.tag, data.template)
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Error Creating Backup. See Log File"),
        )

    return SnackResponse.success("Backup Created in /data/backups")


@router.post(
    "/api/backups/{file_name}/import/", tags=["Import / Export"], status_code=200
)
async def import_database(file_name: str):
    """ Returns this weeks meal plan """
    imported = import_from_archive(file_name)
    return imported


@router.delete(
    "/api/backups/{backup_name}/delete/",
    tags=["Import / Export"],
    status_code=200,
)
async def delete_backup(backup_name: str):
    """ Returns this weeks meal plan """

    try:
        BACKUP_DIR.joinpath(backup_name).unlink()
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Unable to Delete Backup. See Log File"),
        )

    return SnackResponse.success(f"{backup_name} Deleted")
