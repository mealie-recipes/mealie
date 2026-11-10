from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy import delete, select
from sqlalchemy.orm.session import Session

from mealie.core.security import hash_password, url_safe_token
from mealie.db.models.users.password_reset import PasswordResetModel
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user_passwords import PasswordResetTokenSave
from mealie.services._base_service import BaseService
from mealie.services.email import EmailService


class PasswordResetService(BaseService):
    def __init__(self, session: Session) -> None:
        self.db = get_repositories(session, group_id=None, household_id=None)
        super().__init__()

    def generate_reset_token(self, email: str) -> PasswordResetTokenSave | None:
        user = self.db.users.get_one(email, "email", any_case=True)

        if user is None:
            self.logger.error(f"failed to create password reset for {email=}: user doesn't exists")
            # Do not raise exception here as we don't want to confirm to the client that the Email doesn't exists
            return None
        elif user.auth_method == AuthMethod.LDAP:
            self.logger.error(f"failed to create password reset for {email=}: user controlled by LDAP")
            return None

        self._delete_user_tokens(user.id)

        # Create Reset Token
        token = url_safe_token()

        save_token = PasswordResetTokenSave(user_id=user.id, token=token)

        return self.db.tokens_pw_reset.create(save_token)

    def _delete_user_tokens(self, user_id: UUID4) -> None:
        self.db.session.execute(delete(PasswordResetModel).where(PasswordResetModel.user_id == user_id))
        self.db.session.commit()

    def _get_valid_token(self, token: str) -> PasswordResetModel | None:
        token_row = self.db.session.scalars(
            select(PasswordResetModel).where(PasswordResetModel.token == token)
        ).one_or_none()

        lifetime = timedelta(hours=self.settings.PASSWORD_RESET_TOKEN_TIME)
        if token_row is None or datetime.now(UTC) - token_row.created_at > lifetime:
            return None

        return token_row

    def send_reset_email(self, email: str, accept_language: str | None = None) -> None:
        """Never raises: callers run this in the background and must not leak account existence."""
        try:
            token_entry = self.generate_reset_token(email)
            if token_entry is None:
                return

            email_service = EmailService(locale=accept_language)
            reset_url = f"{self.settings.BASE_URL}/reset-password/?token={token_entry.token}"
            email_service.send_forgot_password(email, reset_url)
        except Exception:
            self.logger.exception("failed to send password reset email")

    def reset_password(self, token: str, new_password: str):
        # Validate Token
        token_entry = self._get_valid_token(token)

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

        self._delete_user_tokens(user.id)
