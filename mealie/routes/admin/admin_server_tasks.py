from fastapi import BackgroundTasks

from mealie.routes._base import BaseAdminController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.server.tasks import ServerTask, ServerTaskNames
from mealie.services.server_tasks import BackgroundExecutor, test_executor_func

router = UserAPIRouter()


@controller(router)
class AdminServerTasksController(BaseAdminController):
    @router.get("/server-tasks", response_model=list[ServerTask])
    def get_all(self):
        return self.repos.server_tasks.get_all(order_by="created_at")

    @router.post("/server-tasks", response_model=ServerTask, status_code=201)
    def create_test_tasks(self, bg_tasks: BackgroundTasks):
        bg_executor = BackgroundExecutor(self.group.id, self.repos, bg_tasks)
        return bg_executor.dispatch(ServerTaskNames.default, test_executor_func)
