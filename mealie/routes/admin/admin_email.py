from fastapi import APIRouter
from fastapi_camelcase import CamelModel

from mealie.routes._base import BaseAdminController, controller
from mealie.services.email import EmailService

router = APIRouter(prefix="/email")


class EmailReady(CamelModel):
    ready: bool


class EmailSuccess(CamelModel):
    success: bool
    error: str = None


class EmailTest(CamelModel):
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
