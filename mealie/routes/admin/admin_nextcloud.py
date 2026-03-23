from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema._mealie import MealieModel
from mealie.services.nextcloud.caldav import NextcloudTasksService

router = APIRouter(prefix="/nextcloud")


class NextcloudTestResponse(MealieModel):
    status: str
    message: str | None = None
    calendars: list[dict] | None = None


@controller(router)
class AdminNextcloudController(BaseAdminController):
    @router.post("/test", response_model=NextcloudTestResponse)
    def test_nextcloud_connection(self, url: str, username: str, password: str, task_list: str, verify_ssl: bool = True):
        """Test a Nextcloud CalDAV connection and list available task lists."""
        service = NextcloudTasksService(
            url=url,
            username=username,
            password=password,
            task_list=task_list,
            verify_ssl=verify_ssl,
        )
        result = service.test_connection()
        return NextcloudTestResponse(**result)
