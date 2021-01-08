from fastapi import APIRouter, HTTPException
from models.backup_models import BackupJob, Imports
from pydantic.main import BaseModel
from services.backup_services import (
    BACKUP_DIR,
    TEMPLATE_DIR,
    export_db,
    import_from_archive,
)
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/backups/available/", tags=["Import / Export"], response_model=Imports)
async def available_imports():
    """Returns a list of avaiable .zip files for import into Mealie."""
    imports = []
    templates = []
    for archive in BACKUP_DIR.glob("*.zip"):
        imports.append(archive.name)

    for template in TEMPLATE_DIR.glob("*.md"):
        templates.append(template.name)

    return Imports(imports=imports, templates=templates)


@router.post("/api/backups/export/database/", tags=["Import / Export"], status_code=201)
async def export_database(data: BackupJob):
    """Generates a backup of the recipe database in json format."""
    try:
        export_path = export_db(data.tag, data.template)
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Error Creating Backup. See Log File"),
        )

    return SnackResponse.success("Backup Created at " + export_path)


@router.post(
    "/api/backups/{file_name}/import/", tags=["Import / Export"], status_code=200
)
async def import_database(file_name: str):
    """ Import a database backup file generated from Mealie. """
    imported = import_from_archive(file_name)
    return imported


@router.delete(
    "/api/backups/{backup_name}/delete/",
    tags=["Import / Export"],
    status_code=200,
)
async def delete_backup(backup_name: str):
    """ Removes a database backup from the file system """

    try:
        BACKUP_DIR.joinpath(backup_name).unlink()
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Unable to Delete Backup. See Log File"),
        )

    return SnackResponse.success(f"{backup_name} Deleted")
