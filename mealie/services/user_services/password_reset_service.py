from http.client import HTTPException

from fastapi import status

from mealie.core.root_logger import get_logger
from mealie.services._base_http_service.http_services import PublicHttpService
from mealie.services.email import EmailService

logger = get_logger(__name__)


class PasswordResetService(PublicHttpService[int, str]):
    def populate_item() -> None:
        pass

    def send_reset_email(self, email: str):
        user = self.db.users.get_one(email, "email")

        if user is None:
            logger.error(f"failed to create password reset for {email=}: user doesn't exists")
            # Do not raise exception here as we don't want to confirm to the client that the Email doens't exists
            return

        # Create Reset Token
        token = "my-reset-token"

        # Send Email
        email_servive = EmailService()
        reset_url = f"{self.settings.BASE_URL}/reset-password?token={token}"

        try:
            email_servive.send_forgot_password(email, reset_url)
        except Exception as e:
            logger.error(f"failed to send reset email: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to send reset email")

    def reset_password(self, token: str, new_password: str):
        # Validate Token
        # Update Password
        # Confirm Password
        # Delete Token from DB
        pass
