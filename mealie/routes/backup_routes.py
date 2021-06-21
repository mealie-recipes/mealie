import operator
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from mealie.core.config import app_dirs
from mealie.core.root_logger import get_logger
from mealie.core.security import create_file_token
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_admin_user
from mealie.schema.backup import BackupJob, ImportJob, Imports, LocalBackup
from mealie.services.backups import imports
from mealie.services.backups.exports import backup_all
from mealie.services.events import create_backup_event
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/backups", tags=["Backups"], dependencies=[Depends(get_admin_user)])
logger = get_logger()


@router.get("/available", response_model=Imports)
def available_imports():
    """Returns a list of avaiable .zip files for import into Mealie."""
    imports = []
    for archive in app_dirs.BACKUP_DIR.glob("*.zip"):
        backup = LocalBackup(name=archive.name, date=archive.stat().st_ctime)
        imports.append(backup)

    templates = [template.name for template in app_dirs.TEMPLATE_DIR.glob("*.*")]
    imports.sort(key=operator.attrgetter("date"), reverse=True)

    return Imports(imports=imports, templates=templates)


@router.post("/export/database", status_code=status.HTTP_201_CREATED)
def export_database(background_tasks: BackgroundTasks, data: BackupJob, session: Session = Depends(generate_session)):
    """Generates a backup of the recipe database in json format."""
    try:
        export_path = backup_all(
            session=session,
            tag=data.tag,
            templates=data.templates,
            export_recipes=data.options.recipes,
            export_settings=data.options.settings,
            export_pages=data.options.pages,
            export_themes=data.options.themes,
            export_users=data.options.users,
            export_groups=data.options.groups,
            export_notifications=data.options.notifications,
        )
        background_tasks.add_task(
            create_backup_event, "Database Backup", f"Manual Backup Created '{Path(export_path).name}'", session
        )
        return {"export_path": export_path}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload", status_code=status.HTTP_200_OK)
def upload_backup_file(archive: UploadFile = File(...)):
    """ Upload a .zip File to later be imported into Mealie """
    dest = app_dirs.BACKUP_DIR.joinpath(archive.filename)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    if not dest.is_file:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.get("/{file_name}/download")
async def download_backup_file(file_name: str):
    """ Returns a token to download a file """
    file = app_dirs.BACKUP_DIR.joinpath(file_name)

    return {"fileToken": create_file_token(file)}


@router.post("/{file_name}/import", status_code=status.HTTP_200_OK)
def import_database(
    background_tasks: BackgroundTasks,
    file_name: str,
    import_data: ImportJob,
    session: Session = Depends(generate_session),
):
    """ Import a database backup file generated from Mealie. """

    db_import = imports.import_database(
        session=session,
        archive=import_data.name,
        import_recipes=import_data.recipes,
        import_settings=import_data.settings,
        import_pages=import_data.pages,
        import_themes=import_data.themes,
        import_users=import_data.users,
        import_groups=import_data.groups,
        force_import=import_data.force,
        rebase=import_data.rebase,
    )
    background_tasks.add_task(create_backup_event, "Database Restore", f"Restore File: {file_name}", session)
    return db_import


@router.delete("/{file_name}/delete", status_code=status.HTTP_200_OK)
def delete_backup(file_name: str):
    """ Removes a database backup from the file system """
    file_path = app_dirs.BACKUP_DIR.joinpath(file_name)

    if not file_path.is_file():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    try:
        file_path.unlink()
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
