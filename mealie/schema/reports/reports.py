import datetime
import enum

from pydantic import Field
from pydantic.types import UUID4

from mealie.schema._mealie import MealieModel


class ReportCategory(str, enum.Enum):
    backup = "backup"
    restore = "restore"
    migration = "migration"


class ReportSummaryStatus(str, enum.Enum):
    in_progress = "in-progress"
    success = "success"
    failure = "failure"
    partial = "partial"


class ReportEntryCreate(MealieModel):
    report_id: UUID4
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    success: bool = True
    message: str
    exception: str = ""


class ReportEntryOut(ReportEntryCreate):
    id: UUID4

    class Config:
        orm_mode = True


class ReportCreate(MealieModel):
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    category: ReportCategory
    group_id: UUID4
    name: str
    status: ReportSummaryStatus = ReportSummaryStatus.in_progress


class ReportSummary(ReportCreate):
    id: UUID4


class ReportOut(ReportSummary):
    entries: list[ReportEntryOut] = []

    class Config:
        orm_mode = True
