from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session
from mealie.schema.user.user_passwords import ForgotPassword, ResetPassword
from mealie.services.user_services.password_reset_service import PasswordResetService

router = APIRouter(prefix="")


@router.post("/forgot-password")
def forgot_password(email: ForgotPassword, session: Session = Depends(generate_session)):
    """Sends an email with a reset link to the user"""
    f_service = PasswordResetService(session)
    return f_service.send_reset_email(email.email)


@router.post("/reset-password")
def reset_password(reset_password: ResetPassword, session: Session = Depends(generate_session)):
    """Resets the user password"""
    f_service = PasswordResetService(session)
    return f_service.reset_password(reset_password.token, reset_password.password)
