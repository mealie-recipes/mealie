from random import getrandbits
from time import sleep
from typing import Any, Callable

from sqlalchemy.orm import Session

from mealie.repos.all_repositories import get_repositories
from mealie.schema.server.tasks import ServerTask, ServerTaskCreate, ServerTaskNames

from .._base_http_service.http_services import UserHttpService


class BackgroundExecutor(UserHttpService):
    sleep_time = 60

    def populate_item(self, _: int) -> ServerTask:
        pass

    def dispatch(self, task_name: ServerTaskNames, func: Callable, *args: Any, **kwargs: Any) -> ServerTask:
        """The dispatch function is a wrapper around the BackgroundTasks class in Starlett. It dirctly calls
        the add_task function and your task will be run in the background. This function all passes the id required
        to check on the server tasks in the database and provide updates.

        Tasks that are dispachd by the Background executor should be designed to accept this key word argument
        and update the item in the database accordingly.
        """

        server_task = ServerTaskCreate(group_id=self.group_id, name=task_name)
        server_task = self.db.server_tasks.create(server_task)

        self.background_tasks.add_task(func, *args, **kwargs, task_id=server_task.id, session=self.session)

        return server_task


def test_executor_func(task_id: int, session: Session) -> None:
    database = get_repositories(session)
    task = database.server_tasks.get_one(task_id)

    task.append_log("test task has started")
    task.append_log("test task sleeping for 60 seconds")

    sleep(BackgroundExecutor.sleep_time)

    task.append_log("test task has finished sleep")

    # Randomly Decide to set to failed or not

    is_fail = bool(getrandbits(1))

    if is_fail:
        task.append_log("test task has failed")
        task.set_failed()
    else:
        task.append_log("test task has succeeded")
        task.set_finished()

    database.server_tasks.update(task.id, task)
