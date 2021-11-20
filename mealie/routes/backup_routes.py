import operator
import shutil
from pathlib import Path

from fastapi import BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs

app_dirs = get_app_dirs()
from mealie.core.dependencies import get_current_user
from mealie.core.root_logger import get_logger
from mealie.core.security import create_file_token
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.admin import AllBackups, BackupFile, CreateBackup, ImportJob
from mealie.schema.user.user import PrivateUser
from mealie.services.backups import imports
from mealie.services.backups.exports import backup_all
from mealie.services.events import create_backup_event

router = AdminAPIRouter(prefix="/api/backups", tags=["Backups"])
logger = get_logger()


@router.get("/available", response_model=AllBackups)
def available_imports():
    """Returns a list of avaiable .zip files for import into Mealie."""
    imports = []
    for archive in app_dirs.BACKUP_DIR.glob("*.zip"):
        backup = BackupFile(name=archive.name, date=archive.stat().st_ctime)
        imports.append(backup)

    templates = [template.name for template in app_dirs.TEMPLATE_DIR.glob("*.*")]
    imports.sort(key=operator.attrgetter("date"), reverse=True)

    return AllBackups(imports=imports, templates=templates)


@router.post("/export/database", status_code=status.HTTP_201_CREATED)
def export_database(
    background_tasks: BackgroundTasks, data: CreateBackup, session: Session = Depends(generate_session)
):
    """Generates a backup of the recipe database in json format."""
    try:
        export_path = backup_all(
            session=session,
            tag=data.tag,
            templates=data.templates,
            export_recipes=data.options.recipes,
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
    """Upload a .zip File to later be imported into Mealie"""
    dest = app_dirs.BACKUP_DIR.joinpath(archive.filename)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    if not dest.is_file:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.get("/{file_name}/download")
async def download_backup_file(file_name: str):
    """Returns a token to download a file"""
    file = app_dirs.BACKUP_DIR.joinpath(file_name)

    return {"fileToken": create_file_token(file)}


@router.post("/{file_name}/import", status_code=status.HTTP_200_OK)
def import_database(
    background_tasks: BackgroundTasks,
    file_name: str,
    import_data: ImportJob,
    session: Session = Depends(generate_session),
    user: PrivateUser = Depends(get_current_user),
):
    """Import a database backup file generated from Mealie."""

    db_import = imports.import_database(
        user=user,
        session=session,
        archive=import_data.name,
        import_recipes=import_data.recipes,
        import_settings=import_data.settings,
        import_users=import_data.users,
        import_groups=import_data.groups,
        force_import=import_data.force,
        rebase=import_data.rebase,
    )

    background_tasks.add_task(create_backup_event, "Database Restore", f"Restore File: {file_name}", session)
    return db_import


@router.delete("/{file_name}/delete", status_code=status.HTTP_200_OK)
def delete_backup(file_name: str):
    """Removes a database backup from the file system"""
    file_path = app_dirs.BACKUP_DIR.joinpath(file_name)

    if not file_path.is_file():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    try:
        file_path.unlink()
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
