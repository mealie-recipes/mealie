from abc import ABC, abstractmethod

import emails
from emails.backend.response import SMTPResponse

from mealie.core.root_logger import get_logger
from mealie.services._base_service import BaseService

logger = get_logger()


class ABCEmailSender(ABC):
    @abstractmethod
    def send(self, email_to: str, subject: str, html: str) -> bool:
        ...


class DefaultEmailSender(ABCEmailSender, BaseService):
    def send(self, email_to: str, subject: str, html: str) -> bool:
        message = emails.Message(
            subject=subject,
            html=html,
            mail_from=(self.settings.SMTP_FROM_NAME, self.settings.SMTP_FROM_EMAIL),
        )

        smtp_options = {"host": self.settings.SMTP_HOST, "port": self.settings.SMTP_PORT}
        if self.settings.SMTP_TLS:
            smtp_options["tls"] = True
        if self.settings.SMTP_USER:
            smtp_options["user"] = self.settings.SMTP_USER
        if self.settings.SMTP_PASSWORD:
            smtp_options["password"] = self.settings.SMTP_PASSWORD
        response: SMTPResponse = message.send(to=email_to, smtp=smtp_options)
        logger.info(f"send email result: {response}")

        if not response.success:
            logger.error(f"send email error: {response.error}")

        return response.status_code in [250]
