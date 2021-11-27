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

logger = get_logger(module=__name__)


class GroupMigrationService(UserHttpService[int, ReportOut]):
    event_func = create_group_event
    _restrict_by_group = True
    _schema = ReportOut

    @cached_property
    def dal(self):
        raise NotImplementedError

    def populate_item(self, id: UUID4) -> ReportOut:
        return None

    def migrate(self, migration: SupportedMigrations, archive: Path) -> ReportSummary:
        if migration == SupportedMigrations.nextcloud:
            self.migration_type = NextcloudMigrator(archive, self.db, self.session, self.user.id, self.group_id)

        if migration == SupportedMigrations.chowdown:
            self.migration_type = ChowdownMigrator(archive, self.db, self.session, self.user.id, self.group_id)

        return self.migration_type.migrate(f"{migration.value.title()} Migration")
