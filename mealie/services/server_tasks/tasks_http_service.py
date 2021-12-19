from functools import cached_property

from mealie.schema.server import ServerTask
from mealie.services._base_http_service.http_services import AdminHttpService, UserHttpService


class ServerTasksHttpService(UserHttpService[int, ServerTask]):
    _restrict_by_group = True
    _schema = ServerTask

    @cached_property
    def repo(self):
        return self.db.server_tasks

    def populate_item(self, id: int) -> ServerTask:
        self.item = self.repo.get_one(id)
        return self.item

    def get_all(self) -> list[ServerTask]:
        return self.repo.multi_query(query_by={"group_id": self.group_id}, order_by="created_at")


class AdminServerTasks(AdminHttpService[int, ServerTask]):
    _restrict_by_group = True
    _schema = ServerTask

    @cached_property
    def repo(self):
        return self.db.server_tasks

    def populate_item(self, id: int) -> ServerTask:
        self.item = self.repo.get_one(id)
        return self.item

    def get_all(self) -> list[ServerTask]:
        return self.repo.get_all(order_by="created_at")
