from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.root_logger import get_logger
from mealie.core.security import hash_password, url_safe_token
from mealie.db.database import get_database
from mealie.schema.user.user_passwords import SavePasswordResetToken
from mealie.services._base_service import BaseService
from mealie.services.email import EmailService

logger = get_logger(__name__)


class PasswordResetService(BaseService):
    def __init__(self, session: Session) -> None:
        self.db = get_database(session)
        super().__init__()

    def generate_reset_token(self, email: str) -> SavePasswordResetToken:
        user = self.db.users.get_one(email, "email")

        if user is None:
            logger.error(f"failed to create password reset for {email=}: user doesn't exists")
            # Do not raise exception here as we don't want to confirm to the client that the Email doens't exists
            return

        # Create Reset Token
        token = url_safe_token()

        save_token = SavePasswordResetToken(user_id=user.id, token=token)

        return self.db.tokens_pw_reset.create(save_token)

    def send_reset_email(self, email: str):
        token_entry = self.generate_reset_token(email)

        # Send Email
        email_servive = EmailService()
        reset_url = f"{self.settings.BASE_URL}/reset-password?token={token_entry.token}"

        try:
            email_servive.send_forgot_password(email, reset_url)
        except Exception as e:
            logger.error(f"failed to send reset email: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to send reset email")

    def reset_password(self, token: str, new_password: str):
        # Validate Token
        token_entry = self.db.tokens_pw_reset.get_one(token, "token")

        if token_entry is None:
            logger.error("failed to reset password: invalid token")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token")

        user = self.db.users.get_one(token_entry.user_id)
        # Update Password
        password_hash = hash_password(new_password)

        new_user = self.db.users.update_password(user.id, password_hash)
        # Confirm Password
        if new_user.password != password_hash:
            logger.error("failed to reset password: invalid password")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid password")

        # Delete Token from DB
        self.db.tokens_pw_reset.delete(token_entry.token)
