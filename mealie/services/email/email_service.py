from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel

from mealie.core.root_logger import get_logger
from mealie.lang import local_provider
from mealie.lang.providers import Translator
from mealie.services._base_service import BaseService

from .email_senders import ABCEmailSender, DefaultEmailSender

CWD = Path(__file__).parent

logger = get_logger()


class EmailTemplate(BaseModel):
    subject: str
    header_text: str
    message_top: str
    message_bottom: str
    button_link: str
    button_text: str

    def render_html(self, template: Path) -> str:
        tmpl = Template(template.read_text())

        return tmpl.render(data=self.model_dump())


class EmailService(BaseService):
    def __init__(self, sender: ABCEmailSender | None = None, locale: str | None = None) -> None:
        self.templates_dir = CWD / "templates"
        self.default_template = self.templates_dir / "default.html"
        self.sender: ABCEmailSender = sender or DefaultEmailSender()
        self.translator: Translator = local_provider(locale)

        super().__init__()

    def send_email(self, email_to: str, data: EmailTemplate) -> bool:
        if not self.settings.SMTP_ENABLE:
            return False

        return self.sender.send(email_to, data.subject, data.render_html(self.default_template))

    def send_forgot_password(self, address: str, reset_password_url: str) -> bool:
        forgot_password = EmailTemplate(
            subject=self.translator.t("emails.password.subject"),
            header_text=self.translator.t("emails.password.header_text"),
            message_top=self.translator.t("emails.password.message_top"),
            message_bottom=self.translator.t("emails.password.message_bottom"),
            button_link=reset_password_url,
            button_text=self.translator.t("emails.password.button_text"),
        )
        return self.send_email(address, forgot_password)

    def send_invitation(self, address: str, invitation_url: str) -> bool:
        invitation = EmailTemplate(
            subject=self.translator.t("emails.invitation.subject"),
            header_text=self.translator.t("emails.invitation.header_text"),
            message_top=self.translator.t("emails.invitation.message_top"),
            message_bottom=self.translator.t("emails.invitation.message_bottom"),
            button_link=invitation_url,
            button_text=self.translator.t("emails.invitation.button_text"),
        )
        return self.send_email(address, invitation)

    def send_test_email(self, address: str) -> bool:
        test_email = EmailTemplate(
            subject=self.translator.t("emails.test.subject"),
            header_text=self.translator.t("emails.test.header_text"),
            message_top=self.translator.t("emails.test.message_top"),
            message_bottom=self.translator.t("emails.test.message_bottom"),
            button_link=self.settings.BASE_URL,
            button_text=self.translator.t("emails.test.button_text"),
        )
        return self.send_email(address, test_email)
