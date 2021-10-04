from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel

from mealie.core.root_logger import get_logger
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

        return tmpl.render(data=self.dict())


class EmailService(BaseService):
    def __init__(self, sender: ABCEmailSender = None) -> None:
        self.templates_dir = CWD / "templates"
        self.default_template = self.templates_dir / "default.html"
        self.sender: ABCEmailSender = sender or DefaultEmailSender()

        super().__init__()

    def send_email(self, email_to: str, data: EmailTemplate) -> bool:
        if not self.settings.SMTP_ENABLE:
            return False

        return self.sender.send(email_to, data.subject, data.render_html(self.default_template))

    def send_forgot_password(self, address: str, reset_password_url: str) -> bool:
        forgot_password = EmailTemplate(
            subject="Mealie Forgot Password",
            header_text="Forgot Password",
            message_top="You have requested to reset your password.",
            message_bottom="Please click the button below to reset your password.",
            button_link=reset_password_url,
            button_text="Reset Password",
        )
        return self.send_email(address, forgot_password)

    def send_invitation(self, address: str, invitation_url: str) -> bool:
        invitation = EmailTemplate(
            subject="Invitation to join Mealie",
            header_text="Invitation",
            message_top="You have been invited to join Mealie.",
            message_bottom="Please click the button below to accept the invitation.",
            button_link=invitation_url,
            button_text="Accept Invitation",
        )
        return self.send_email(address, invitation)

    def send_test_email(self, address: str) -> bool:
        test_email = EmailTemplate(
            subject="Test Email",
            header_text="Test Email",
            message_top="This is a test email.",
            message_bottom="Please click the button below to test the email.",
            button_link="https://www.google.com",
            button_text="Test Email",
        )
        return self.send_email(address, test_email)


def main():
    print("Starting...")
    service = EmailService()
    service.send_test_email("hay-kot@pm.me")
    print("Finished...")


if __name__ == "__main__":
    main()
