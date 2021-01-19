import operator

from app_config import BACKUP_DIR, TEMPLATE_DIR
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, HTTPException
from models.backup_models import BackupJob, ImportJob, Imports, LocalBackup
from services.backups.exports import backup_all
from services.backups.imports import ImportDatabase
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(tags=["Import / Export"])


@router.get("/api/backups/available/", response_model=Imports)
def available_imports():
    """Returns a list of avaiable .zip files for import into Mealie."""
    imports = []
    templates = []
    for archive in BACKUP_DIR.glob("*.zip"):
        backup = LocalBackup(name=archive.name, date=archive.stat().st_ctime)
        imports.append(backup)

    for template in TEMPLATE_DIR.glob("*.*"):
        templates.append(template.name)

    imports.sort(key=operator.attrgetter("date"), reverse=True)

    return Imports(imports=imports, templates=templates)


@router.post("/api/backups/export/database/", status_code=201)
def export_database(data: BackupJob, db: Session = Depends(generate_session)):
    """Generates a backup of the recipe database in json format."""
    export_path = backup_all(
        session=db,
        tag=data.tag,
        templates=data.templates,
        export_recipes=data.options.recipes,
        export_settings=data.options.settings,
        export_themes=data.options.themes,
    )
    try:
        return SnackResponse.success("Backup Created at " + export_path)
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Error Creating Backup. See Log File"),
        )


@router.post("/api/backups/{file_name}/import/", status_code=200)
def import_database(
    file_name: str, import_data: ImportJob, db: Session = Depends(generate_session)
):
    """ Import a database backup file generated from Mealie. """

    import_db = ImportDatabase(
        session=db,
        zip_archive=import_data.name,
        import_recipes=import_data.recipes,
        force_import=import_data.force,
        rebase=import_data.rebase,
        import_settings=import_data.settings,
        import_themes=import_data.themes,
    )

    imported = import_db.run()
    return imported


@router.delete(
    "/api/backups/{backup_name}/delete/",
    tags=["Import / Export"],
    status_code=200,
)
def delete_backup(backup_name: str):
    """ Removes a database backup from the file system """

    try:
        BACKUP_DIR.joinpath(backup_name).unlink()
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Unable to Delete Backup. See Log File"),
        )

    return SnackResponse.success(f"{backup_name} Deleted")
