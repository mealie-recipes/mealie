import operator
import shutil

from core.config import BACKUP_DIR, TEMPLATE_DIR
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from schema.backup import BackupJob, ImportJob, Imports, LocalBackup
from services.backups.exports import backup_all
from services.backups.imports import ImportDatabase
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse
from schema.snackbar import SnackResponse

router = APIRouter(prefix="/api/backups", tags=["Backups"])


@router.get("/available", response_model=Imports)
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


@router.post("/export/database", status_code=201)
def export_database(data: BackupJob, session: Session = Depends(generate_session)):
    """Generates a backup of the recipe database in json format."""
    export_path = backup_all(
        session=session,
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


@router.post("/upload")
def upload_backup_zipfile(archive: UploadFile = File(...)):
    """ Upload a .zip File to later be imported into Mealie """
    dest = BACKUP_DIR.joinpath(archive.filename)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    if dest.is_file:
        return SnackResponse.success("Backup uploaded")
    else:
        return SnackResponse.error("Failure uploading file")


@router.get("/{file_name}/download")
async def upload_nextcloud_zipfile(file_name: str):
    """ Upload a .zip File to later be imported into Mealie """
    file = BACKUP_DIR.joinpath(file_name)

    if file.is_file:
        return FileResponse(
            file, media_type="application/octet-stream", filename=file_name
        )
    else:
        return SnackResponse.error("No File Found")


@router.post("/{file_name}/import", status_code=200)
def import_database(
    file_name: str, import_data: ImportJob, session: Session = Depends(generate_session)
):
    """ Import a database backup file generated from Mealie. """

    import_db = ImportDatabase(
        session=session,
        zip_archive=import_data.name,
        import_recipes=import_data.recipes,
        force_import=import_data.force,
        rebase=import_data.rebase,
        import_settings=import_data.settings,
        import_themes=import_data.themes,
    )

    imported = import_db.run()
    return imported


@router.delete("/{file_name}/delete", status_code=200)
def delete_backup(file_name: str):
    """ Removes a database backup from the file system """

    try:
        BACKUP_DIR.joinpath(file_name).unlink()
    except:
        HTTPException(
            status_code=400,
            detail=SnackResponse.error("Unable to Delete Backup. See Log File"),
        )

    return SnackResponse.error(f"{file_name} Deleted")
