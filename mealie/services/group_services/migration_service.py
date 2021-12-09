from __future__ import annotations

from functools import cached_property
from pathlib import Path

from pydantic.types import UUID4

from mealie.core.root_logger import get_logger
from mealie.schema.group.group_migration import SupportedMigrations
from mealie.schema.reports.reports import ReportOut, ReportSummary
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event
from mealie.services.migrations import ChowdownMigrator, NextcloudMigrator
from mealie.services.migrations.mealie_alpha import MealieAlphaMigrator
from mealie.services.migrations.paprika import PaprikaMigrator

logger = get_logger(module=__name__)


class GroupMigrationService(UserHttpService[int, ReportOut]):
    event_func = create_group_event
    _restrict_by_group = True
    _schema = ReportOut

    @cached_property
    def dal(self):
        raise NotImplementedError

    def populate_item(self, _: UUID4) -> ReportOut:
        return None

    def migrate(self, migration: SupportedMigrations, add_migration_tag: bool, archive: Path) -> ReportSummary:
        args = {
            "archive": archive,
            "db": self.db,
            "session": self.session,
            "user_id": self.user.id,
            "group_id": self.group_id,
            "add_migration_tag": add_migration_tag,
        }

        if migration == SupportedMigrations.nextcloud:
            self.migration_type = NextcloudMigrator(**args)

        if migration == SupportedMigrations.chowdown:
            self.migration_type = ChowdownMigrator(**args)

        if migration == SupportedMigrations.paprika:
            self.migration_type = PaprikaMigrator(**args)

        if migration == SupportedMigrations.mealie_alpha:
            self.migration_type = MealieAlphaMigrator(**args)

        return self.migration_type.migrate(f"{migration.value.title()} Migration")
