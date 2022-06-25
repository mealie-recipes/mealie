import datetime
import enum
from uuid import UUID

from pydantic import Field

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class ServerTaskNames(str, enum.Enum):
    default = "Background Task"
    backup_task = "Database Backup"
    bulk_recipe_import = "Bulk Recipe Import"


class ServerTaskStatus(str, enum.Enum):
    running = "running"
    finished = "finished"
    failed = "failed"


class ServerTaskCreate(MealieModel):
    group_id: UUID
    name: ServerTaskNames = ServerTaskNames.default
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    status: ServerTaskStatus = ServerTaskStatus.running
    log: str = ""

    def set_running(self) -> None:
        self.status = ServerTaskStatus.running

    def set_finished(self) -> None:
        self.status = ServerTaskStatus.finished

    def set_failed(self) -> None:
        self.status = ServerTaskStatus.failed

    def append_log(self, message: str) -> None:
        # Prefix with Timestamp and append new line and join to log
        self.log += f"{datetime.datetime.now()}: {message}\n"


class ServerTask(ServerTaskCreate):
    id: int

    class Config:
        orm_mode = True


class ServerTaskPagination(PaginationBase):
    items: list[ServerTask]
