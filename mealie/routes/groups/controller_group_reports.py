from functools import cached_property

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.reports.reports import ReportCategory, ReportCreate, ReportOut, ReportSummary
from mealie.schema.response.responses import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/groups/reports", tags=["Groups: Reports"])


@controller(router)
class GroupReportsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.group_reports

    def registered_exceptions(self, ex: type[Exception]) -> str:
        return {
            **mealie_registered_exceptions(self.translator),
        }.get(ex, self.t("generic.server-error"))

    @cached_property
    def mixins(self):
        return HttpRepo[ReportCreate, ReportOut, ReportCreate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=list[ReportSummary])
    def get_all(self, report_type: ReportCategory | None = None):
        return self.repo.multi_query({"group_id": self.group_id, "category": report_type}, limit=9999)

    @router.get("/{item_id}", response_model=ReportOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.delete("/{item_id}", status_code=200)
    def delete_one(self, item_id: UUID4):
        try:
            self.mixins.delete_one(item_id)  # type: ignore
            return SuccessResponse.respond(self.t("group.report-deleted"))
        except Exception as ex:
            raise HTTPException(500, ErrorResponse.respond("Failed to delete report")) from ex
