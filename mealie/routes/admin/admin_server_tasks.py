from fastapi import BackgroundTasks, Depends

from mealie.routes._base import BaseAdminController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.server.tasks import ServerTask, ServerTaskNames, ServerTaskPagination
from mealie.services.server_tasks import BackgroundExecutor, test_executor_func

router = UserAPIRouter()


@controller(router)
class AdminServerTasksController(BaseAdminController):
    @router.get("/server-tasks", response_model=ServerTaskPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repos.server_tasks.page_all(
            pagination=q,
            override=ServerTask,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.dict())
        return response

    @router.post("/server-tasks", response_model=ServerTask, status_code=201)
    def create_test_tasks(self, bg_tasks: BackgroundTasks):
        bg_executor = BackgroundExecutor(self.group.id, self.repos, bg_tasks)
        return bg_executor.dispatch(ServerTaskNames.default, test_executor_func)
