import shutil

from fastapi import Depends, File, Form
from fastapi.datastructures import UploadFile

from mealie.core.dependencies import temporary_zip_path
from mealie.routes.routers import UserAPIRouter
from mealie.schema.group.group_migration import SupportedMigrations
from mealie.schema.reports.reports import ReportSummary
from mealie.services.group_services.migration_service import GroupMigrationService

router = UserAPIRouter()


@router.post("", response_model=ReportSummary)
def start_data_migration(
    migration_type: SupportedMigrations = Form(...),
    archive: UploadFile = File(...),
    temp_path: str = Depends(temporary_zip_path),
    gm_service: GroupMigrationService = Depends(GroupMigrationService.private),
):
    # Save archive to temp_path
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    return gm_service.migrate(migration_type, temp_path)
