import base64
import hmac

import pytest

from mealie.core.config import get_app_settings
from mealie.services.email import EmailService
from mealie.services.email.email_senders import ABCEmailSender, UTF8AuthSMTP

FAKE_ADDRESS = "my_secret_email@example.com"

SUBJECTS = {"Mealie Forgot Password", "Invitation to join Mealie", "Mealie Test Email"}

NON_ASCII_USER = "jürgen@mealie.io"
NON_ASCII_PASSWORD = "pa€ssword"


class TestEmailSender(ABCEmailSender):
    def send(self, email_to: str, subject: str, html: str) -> bool:
        # check email_to:
        assert email_to == FAKE_ADDRESS

        # check subject:
        assert subject in SUBJECTS

        # check html is rendered:
        assert "{{" not in html
        assert "}}" not in html

        return True


class FakeSMTPServer(UTF8AuthSMTP):
    """Replays scripted server replies instead of connecting to a real SMTP server"""

    def __init__(self, auth_mechanism: str, replies: list[tuple[int, bytes]]):
        super().__init__()  # no host, so nothing is connected
        self.esmtp_features = {"auth": auth_mechanism}
        self.replies = replies
        self.commands: list[str] = []

    def ehlo_or_helo_if_needed(self) -> None:
        pass

    def docmd(self, cmd: str, args: str = "") -> tuple[int, bytes]:
        self.commands.append(f"{cmd} {args}".strip())
        return self.replies.pop(0)


def b64(value: str | bytes) -> str:
    return base64.b64encode(value.encode("utf-8") if isinstance(value, str) else value).decode("ascii")


def patch_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "email.mealie.io")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "TLS")
    monkeypatch.setenv("SMTP_FROM_NAME", "Mealie")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_USER", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_PASSWORD", "mealie-password")


@pytest.fixture()
def email_service(monkeypatch) -> EmailService:
    patch_env(monkeypatch)
    email_service = EmailService(TestEmailSender())
    get_app_settings.cache_clear()
    email_service.settings = get_app_settings()
    return email_service


def test_email_disabled(monkeypatch):
    email_service = EmailService(TestEmailSender())

    monkeypatch.setenv("SMTP_HOST", "")  # disable email

    get_app_settings.cache_clear()
    email_service.settings = get_app_settings()
    success = email_service.send_test_email(FAKE_ADDRESS)
    assert not success


def test_test_email(email_service):
    success = email_service.send_test_email(FAKE_ADDRESS)
    assert success


def test_forgot_password_email(email_service):
    success = email_service.send_forgot_password(FAKE_ADDRESS, "https://password-url.com")
    assert success


def test_invitation_email(email_service):
    success = email_service.send_invitation(FAKE_ADDRESS, "https://invitie-url.com")
    assert success


def test_smtp_login_plain_non_ascii_credentials():
    server = FakeSMTPServer("PLAIN", replies=[(235, b"Authentication successful")])

    server.login(NON_ASCII_USER, NON_ASCII_PASSWORD)

    assert server.commands == [f"AUTH PLAIN {b64(f'\0{NON_ASCII_USER}\0{NON_ASCII_PASSWORD}')}"]


def test_smtp_login_login_non_ascii_credentials():
    server = FakeSMTPServer(
        "LOGIN",
        replies=[(334, b64("Password:").encode()), (235, b"Authentication successful")],
    )

    server.login(NON_ASCII_USER, NON_ASCII_PASSWORD)

    assert server.commands == [f"AUTH LOGIN {b64(NON_ASCII_USER)}", b64(NON_ASCII_PASSWORD)]


def test_smtp_login_cram_md5_non_ascii_credentials():
    challenge = b"<1896.697170952@mealie.io>"
    server = FakeSMTPServer(
        "CRAM-MD5",
        replies=[(334, b64(challenge).encode()), (235, b"Authentication successful")],
    )

    server.login(NON_ASCII_USER, NON_ASCII_PASSWORD)

    digest = hmac.HMAC(NON_ASCII_PASSWORD.encode("utf-8"), challenge, "md5").hexdigest()
    assert server.commands == ["AUTH CRAM-MD5", b64(f"{NON_ASCII_USER} {digest}")]
