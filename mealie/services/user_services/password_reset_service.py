from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.security import hash_password, url_safe_token
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user_passwords import SavePasswordResetToken
from mealie.services._base_service import BaseService
from mealie.services.email import EmailService


class PasswordResetService(BaseService):
    def __init__(self, session: Session) -> None:
        self.db = get_repositories(session, group_id=None, household_id=None)
        super().__init__()

    def generate_reset_token(self, email: str) -> SavePasswordResetToken | None:
        user = self.db.users.get_one(email, "email", any_case=True)

        if user is None:
            self.logger.error(f"failed to create password reset for {email=}: user doesn't exists")
            # Do not raise exception here as we don't want to confirm to the client that the Email doesn't exists
            return None
        elif user.password == "LDAP" or user.auth_method == AuthMethod.LDAP:
            self.logger.error(f"failed to create password reset for {email=}: user controlled by LDAP")
            return None

        # Create Reset Token
        token = url_safe_token()

        save_token = SavePasswordResetToken(user_id=user.id, token=token)

        return self.db.tokens_pw_reset.create(save_token)

    def send_reset_email(self, email: str, accept_language: str | None = None):
        token_entry = self.generate_reset_token(email)

        if token_entry is None:
            return None

        # Send Email
        email_servive = EmailService(locale=accept_language)
        reset_url = f"{self.settings.BASE_URL}/reset-password/?token={token_entry.token}"

        try:
            email_servive.send_forgot_password(email, reset_url)
        except Exception as e:
            self.logger.error(f"failed to send reset email: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to send reset email") from e

    def reset_password(self, token: str, new_password: str):
        # Validate Token
        token_entry = self.db.tokens_pw_reset.get_one(token, "token")

        if token_entry is None:
            self.logger.error("failed to reset password: invalid token")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token")

        user = self.db.users.get_one(token_entry.user_id)
        # Update Password
        password_hash = hash_password(new_password)

        new_user = self.db.users.update_password(user.id, password_hash)
        # Confirm Password
        if new_user.password != password_hash:
            self.logger.error("failed to reset password: invalid password")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid password")

        # Delete Token from DB
        self.db.tokens_pw_reset.delete(token_entry.token)
