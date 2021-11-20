from fastapi import APIRouter
from fastapi_camelcase import CamelModel

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.services.email import EmailService

logger = get_logger(__name__)

router = APIRouter(prefix="/email")


class EmailReady(CamelModel):
    ready: bool


class EmailSuccess(CamelModel):
    success: bool
    error: str = None


class EmailTest(CamelModel):
    email: str


@router.get("", response_model=EmailReady)
async def check_email_config():
    """Get general application information"""
    settings = get_app_settings()

    return EmailReady(ready=settings.SMTP_ENABLE)


@router.post("", response_model=EmailSuccess)
async def send_test_email(data: EmailTest):
    service = EmailService()
    status = False
    error = None

    try:
        status = service.send_test_email(data.email)
    except Exception as e:
        logger.error(e)
        error = str(e)

    return EmailSuccess(success=status, error=error)
