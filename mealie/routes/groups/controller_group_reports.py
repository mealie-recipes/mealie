from functools import cached_property
from typing import Type

from fastapi import APIRouter
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.reports.reports import ReportCategory, ReportCreate, ReportOut, ReportSummary

router = APIRouter(prefix="/groups/reports", tags=["Groups: Reports"])


@controller(router)
class GroupReportsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.deps.repos.group_reports.by_group(self.deps.acting_user.group_id)

    def registered_exceptions(self, ex: Type[Exception]) -> str:
        return {
            **mealie_registered_exceptions(self.deps.t),
        }.get(ex, "An unexpected error occurred.")

    @cached_property
    def mixins(self):
        return CrudMixins[ReportCreate, ReportOut, ReportCreate](
            self.repo,
            self.deps.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=list[ReportSummary])
    def get_all(self, report_type: ReportCategory = None):
        return self.repo.multi_query({"group_id": self.group_id, "category": report_type}, limit=9999)

    @router.get("/{item_id}", response_model=ReportOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.delete("/{item_id}", status_code=204)
    def delete_one(self, item_id: UUID4):
        self.mixins.delete_one(item_id)  # type: ignore
