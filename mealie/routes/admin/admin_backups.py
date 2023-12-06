import operator
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from mealie.core.config import get_app_dirs
from mealie.core.root_logger import get_logger
from mealie.core.security import create_file_token
from mealie.pkgs.stats.fs_stats import pretty_size
from mealie.routes._base import BaseAdminController, controller
from mealie.schema.admin.backup import AllBackups, BackupFile
from mealie.schema.response.responses import ErrorResponse, FileTokenResponse, SuccessResponse
from mealie.services.backups_v2.backup_v2 import BackupSchemaMismatch, BackupV2

logger = get_logger()
router = APIRouter(prefix="/backups")


@controller(router)
class AdminBackupController(BaseAdminController):
    def _backup_path(self, name) -> Path:
        return get_app_dirs().BACKUP_DIR / name

    @router.get("", response_model=AllBackups)
    def get_all(self):
        app_dirs = get_app_dirs()
        imports = []
        for archive in app_dirs.BACKUP_DIR.glob("*.zip"):
            backup = BackupFile(
                name=archive.name, date=archive.stat().st_mtime, size=pretty_size(archive.stat().st_size)
            )
            imports.append(backup)

        templates = [template.name for template in app_dirs.TEMPLATE_DIR.glob("*.*")]
        imports.sort(key=operator.attrgetter("date"), reverse=True)

        return AllBackups(imports=imports, templates=templates)

    @router.post("", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse)
    def create_one(self):
        backup = BackupV2()

        try:
            backup.backup()
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR) from e

        return SuccessResponse.respond("Backup created successfully")

    @router.get("/{file_name}", response_model=FileTokenResponse)
    def get_one(self, file_name: str):
        """Returns a token to download a file"""
        file = self._backup_path(file_name)

        if not file.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        return FileTokenResponse.respond(create_file_token(file))

    @router.delete("/{file_name}", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
    def delete_one(self, file_name: str):
        file = self._backup_path(file_name)

        if not file.is_file():
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
        try:
            file.unlink()
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR) from e

        return SuccessResponse.respond(f"{file_name} has been deleted.")

    @router.post("/upload", response_model=SuccessResponse)
    def upload_one(self, archive: UploadFile = File(...)):
        """Upload a .zip File to later be imported into Mealie"""
        if "." not in archive.filename:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        if archive.filename.split(".")[-1] != "zip":
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        name = Path(archive.filename).stem

        app_dirs = get_app_dirs()
        dest = app_dirs.BACKUP_DIR.joinpath(f"{name}.zip")

        if dest.absolute().parent != app_dirs.BACKUP_DIR:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        with dest.open("wb") as buffer:
            shutil.copyfileobj(archive.file, buffer)

        if not dest.is_file():
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

    @router.post("/{file_name}/restore", response_model=SuccessResponse)
    def import_one(self, file_name: str):
        backup = BackupV2()

        file = self._backup_path(file_name)

        try:
            backup.restore(file)
        except BackupSchemaMismatch as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("database backup schema version does not match current database"),
            ) from e
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR) from e

        return SuccessResponse.respond("Restore successful")
