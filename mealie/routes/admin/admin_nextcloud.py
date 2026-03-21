from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema._mealie import MealieModel
from mealie.services.nextcloud.caldav import NextcloudTasksService

router = APIRouter(prefix="/nextcloud")


class NextcloudTestResponse(MealieModel):
    status: str
    message: str | None = None
    calendars: list[dict] | None = None


class NextcloudConfigResponse(MealieModel):
    enabled: bool
    url: str | None = None
    username: str | None = None
    task_list: str | None = None


@controller(router)
class AdminNextcloudController(BaseAdminController):
    @router.get("", response_model=NextcloudConfigResponse)
    def get_nextcloud_config(self):
        """Get current Nextcloud configuration status (without secrets)."""
        return NextcloudConfigResponse(
            enabled=self.settings.NEXTCLOUD_ENABLED,
            url=self.settings.NEXTCLOUD_URL,
            username=self.settings.NEXTCLOUD_USERNAME,
            task_list=self.settings.NEXTCLOUD_TASK_LIST,
        )

    @router.post("/test", response_model=NextcloudTestResponse)
    async def test_nextcloud_connection(self):
        """Test Nextcloud CalDAV connection and list available task lists."""
        if not self.settings.NEXTCLOUD_ENABLED:
            return NextcloudTestResponse(
                status="error",
                message="Nextcloud is not configured. Set NEXTCLOUD_URL, NEXTCLOUD_USERNAME, "
                "NEXTCLOUD_PASSWORD, and NEXTCLOUD_TASK_LIST environment variables.",
            )

        service = NextcloudTasksService(
            url=self.settings.NEXTCLOUD_URL,  # type: ignore
            username=self.settings.NEXTCLOUD_USERNAME,  # type: ignore
            password=self.settings.NEXTCLOUD_PASSWORD,  # type: ignore
            task_list=self.settings.NEXTCLOUD_TASK_LIST,  # type: ignore
            verify_ssl=self.settings.NEXTCLOUD_VERIFY_SSL,
        )

        result = await service.test_connection()
        return NextcloudTestResponse(**result)
