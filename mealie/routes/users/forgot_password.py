from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session, session_context
from mealie.schema.user.user_passwords import ForgotPassword, ResetPassword
from mealie.services.user_services.password_reset_service import PasswordResetService

router = APIRouter(prefix="")


def _send_reset_email(email: str, accept_language: str | None) -> None:
    # The request session is closed once the response is sent, so the task opens its own.
    with session_context() as session:
        PasswordResetService(session).send_reset_email(email, accept_language)


@router.post("/forgot-password")
def forgot_password(
    email: ForgotPassword,
    bg_tasks: BackgroundTasks,
    accept_language: Annotated[str | None, Header()] = None,
):
    """Sends an email with a reset link to the user"""
    # Token creation and the SMTP send run after the response so that timing and status
    # codes do not reveal whether the email belongs to an account.
    bg_tasks.add_task(_send_reset_email, email.email, accept_language)


@router.post("/reset-password")
def reset_password(reset_password: ResetPassword, session: Session = Depends(generate_session)):
    """Resets the user password"""
    f_service = PasswordResetService(session)
    return f_service.reset_password(reset_password.token, reset_password.password)
