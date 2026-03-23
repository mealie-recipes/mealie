from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema._mealie import MealieModel
from mealie.services.nextcloud.caldav import NextcloudTasksService

router = APIRouter(prefix="/nextcloud")


class NextcloudTestRequest(MealieModel):
    url: str
    username: str
    password: str
    task_list: str = ""
    verify_ssl: bool = True


class NextcloudTestResponse(MealieModel):
    status: str
    message: str | None = None
    calendars: list[dict] | None = None


@controller(router)
class AdminNextcloudController(BaseAdminController):
    @router.post("/test", response_model=NextcloudTestResponse)
    def test_nextcloud_connection(self, data: NextcloudTestRequest):
        """Test a Nextcloud CalDAV connection and list available task lists."""
        service = NextcloudTasksService(
            url=data.url,
            username=data.username,
            password=data.password,
            task_list=data.task_list,
            verify_ssl=data.verify_ssl,
        )
        result = service.test_connection()
        return NextcloudTestResponse(**result)
