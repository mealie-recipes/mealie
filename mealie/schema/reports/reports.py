import datetime
import enum

from pydantic import ConfigDict, Field
from pydantic.types import UUID4
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group import ReportModel
from mealie.schema._mealie import MealieModel


def _get_now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


class ReportCategory(str, enum.Enum):
    backup = "backup"
    restore = "restore"
    migration = "migration"
    bulk_import = "bulk_import"


class ReportSummaryStatus(str, enum.Enum):
    in_progress = "in-progress"
    success = "success"
    failure = "failure"
    partial = "partial"


class ReportEntryCreate(MealieModel):
    report_id: UUID4
    timestamp: datetime.datetime = Field(default_factory=_get_now_utc)
    success: bool = True
    message: str
    exception: str = ""


class ReportEntryOut(ReportEntryCreate):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)


class ReportCreate(MealieModel):
    timestamp: datetime.datetime = Field(default_factory=_get_now_utc)
    category: ReportCategory
    group_id: UUID4
    name: str
    status: ReportSummaryStatus = ReportSummaryStatus.in_progress


class ReportSummary(ReportCreate):
    id: UUID4


class ReportOut(ReportSummary):
    entries: list[ReportEntryOut] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(ReportModel.entries)]
