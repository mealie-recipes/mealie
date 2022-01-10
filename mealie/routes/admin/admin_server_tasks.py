from fastapi import Depends

from mealie.routes._base import BaseAdminController, controller
from mealie.routes.routers import UserAPIRouter
from mealie.schema.server.tasks import ServerTask, ServerTaskNames
from mealie.services.server_tasks import BackgroundExecutor, test_executor_func
from mealie.services.server_tasks.tasks_http_service import AdminServerTasks

router = UserAPIRouter()


@controller(router)
class AdminServerTasksController(BaseAdminController):
    @router.get("/server-tasks", response_model=list[ServerTask])
    def get_all_tasks(self, tasks_service: AdminServerTasks = Depends(AdminServerTasks.private)):
        return tasks_service.get_all()

    @router.post("/server-tasks", response_model=ServerTask)
    def create_test_tasks(self, bg_executor: BackgroundExecutor = Depends(BackgroundExecutor.private)):
        return bg_executor.dispatch(ServerTaskNames.default, test_executor_func)
