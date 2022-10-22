import smtplib
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email import message

from mealie.services._base_service import BaseService


@dataclass(slots=True)
class EmailOptions:
    host: str
    port: int
    username: str = None
    password: str = None
    tls: bool = False
    ssl: bool = False


@dataclass(slots=True)
class SMTPResponse:
    success: bool
    message: str
    errors: typing.Any


@dataclass(slots=True)
class Message:
    subject: str
    html: str
    mail_from: tuple[str, str]

    def send(self, to: str, smtp: EmailOptions) -> SMTPResponse:
        msg = message.EmailMessage()
        msg["Subject"] = self.subject
        msg["From"] = self.mail_from
        msg["To"] = to
        msg.add_alternative(self.html, subtype="html")

        if smtp.ssl:
            with smtplib.SMTP_SSL(smtp.host, smtp.port) as server:
                server.login(smtp.username, smtp.password)
                errors = server.send_message(msg)
        else:
            with smtplib.SMTP(smtp.host, smtp.port) as server:
                if smtp.tls:
                    server.starttls()
                if smtp.username and smtp.password:
                    server.login(smtp.username, smtp.password)
                errors = server.send_message(msg)

        return SMTPResponse(errors == {}, "Message Sent", errors=errors)


class ABCEmailSender(ABC):
    @abstractmethod
    def send(self, email_to: str, subject: str, html: str) -> bool:
        ...


class DefaultEmailSender(ABCEmailSender, BaseService):
    """
    DefaultEmailSender is the default email sender for Mealie. It uses the SMTP settings
    from the config file to send emails via the python standard library. It supports
    both TLS and SSL connections.
    """

    def send(self, email_to: str, subject: str, html: str) -> bool:
        message = Message(
            subject=subject,
            html=html,
            mail_from=(self.settings.SMTP_FROM_NAME, self.settings.SMTP_FROM_EMAIL),
        )

        smtp_options = EmailOptions(
            self.settings.SMTP_HOST,
            int(self.settings.SMTP_PORT),
            tls=self.settings.SMTP_AUTH_STRATEGY.upper() == "TLS",
            ssl=self.settings.SMTP_AUTH_STRATEGY.upper() == "SSL",
        )

        if self.settings.SMTP_USER:
            smtp_options.username = self.settings.SMTP_USER
        if self.settings.SMTP_PASSWORD:
            smtp_options.password = self.settings.SMTP_PASSWORD

        response = message.send(to=email_to, smtp=smtp_options)
        self.logger.info(f"send email result: {response}")

        if not response.success:
            self.logger.error(f"send email error: {response}")

        return response.success
