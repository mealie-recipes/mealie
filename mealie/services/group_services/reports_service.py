from __future__ import annotations

from functools import cached_property

from mealie.core.root_logger import get_logger
from mealie.schema.reports.reports import ReportCategory, ReportCreate, ReportOut, ReportSummary
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class GroupReportService(CrudHttpMixins[ReportOut, ReportCreate, ReportCreate], UserHttpService[int, ReportOut]):
    event_func = create_group_event
    _restrict_by_group = True
    _schema = ReportOut

    @cached_property
    def repo(self):
        return self.db.group_reports

    def populate_item(self, id: int) -> ReportOut:
        self.item = self.repo.get_one(id)
        return self.item

    def _get_all(self, report_type: ReportCategory = None) -> list[ReportSummary]:
        return self.repo.multi_query({"group_id": self.group_id, "category": report_type}, limit=9999)

    def delete_one(self, id: int = None) -> ReportOut:
        return self._delete_one(id)
