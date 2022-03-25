from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema._mealie import MealieModel
from mealie.services.email import EmailService

router = APIRouter(prefix="/email")


class EmailReady(MealieModel):
    ready: bool


class EmailSuccess(MealieModel):
    success: bool
    error: str = None


class EmailTest(MealieModel):
    email: str


@controller(router)
class AdminEmailController(BaseAdminController):
    @router.get("", response_model=EmailReady)
    async def check_email_config(self):
        """Get general application information"""
        return EmailReady(ready=self.deps.settings.SMTP_ENABLE)

    @router.post("", response_model=EmailSuccess)
    async def send_test_email(self, data: EmailTest):
        service = EmailService()
        status = False
        error = None

        try:
            status = service.send_test_email(data.email)
        except Exception as e:
            self.deps.logger.error(e)
            error = str(e)

        return EmailSuccess(success=status, error=error)
