import shutil
from pathlib import Path

from fastapi import Depends, File, Form
from fastapi.datastructures import UploadFile

from mealie.core.dependencies import temporary_zip_path
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.group.group_migration import SupportedMigrations
from mealie.schema.reports.reports import ReportSummary
from mealie.services.migrations import (
    BaseMigrator,
    ChowdownMigrator,
    CopyMeThatMigrator,
    MealieAlphaMigrator,
    NextcloudMigrator,
    PaprikaMigrator,
    TandoorMigrator,
)

router = UserAPIRouter(prefix="/groups/migrations", tags=["Group: Migrations"])


@controller(router)
class GroupMigrationController(BaseUserController):
    @router.post("", response_model=ReportSummary)
    def start_data_migration(
        self,
        add_migration_tag: bool = Form(False),
        migration_type: SupportedMigrations = Form(...),
        archive: UploadFile = File(...),
        temp_path: Path = Depends(temporary_zip_path),
    ):
        # Save archive to temp_path
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(archive.file, buffer)

        args = {
            "archive": temp_path,
            "db": self.repos,
            "session": self.session,
            "user_id": self.user.id,
            "group_id": self.group_id,
            "add_migration_tag": add_migration_tag,
        }

        table: dict[SupportedMigrations, type[BaseMigrator]] = {
            SupportedMigrations.chowdown: ChowdownMigrator,
            SupportedMigrations.copymethat: CopyMeThatMigrator,
            SupportedMigrations.mealie_alpha: MealieAlphaMigrator,
            SupportedMigrations.nextcloud: NextcloudMigrator,
            SupportedMigrations.paprika: PaprikaMigrator,
            SupportedMigrations.tandoor: TandoorMigrator,
        }

        constructor = table.get(migration_type, None)

        if constructor is None:
            raise ValueError(f"Unsupported migration type: {migration_type}")

        migrator = constructor(**args)

        return migrator.migrate(f"{migration_type.value.title()} Migration")
