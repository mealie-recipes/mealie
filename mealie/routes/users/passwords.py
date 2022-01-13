from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.core.security import hash_password
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import ChangePassword
from mealie.schema.user.user_passwords import ForgotPassword, ResetPassword
from mealie.services.user_services import UserService
from mealie.services.user_services.password_reset_service import PasswordResetService

user_router = UserAPIRouter(prefix="")
public_router = APIRouter(prefix="")
settings = get_app_settings()


@user_router.put("/{id}/reset-password")
async def reset_user_password(id: int, session: Session = Depends(generate_session)):
    new_password = hash_password(settings.DEFAULT_PASSWORD)

    db = get_repositories(session)
    db.users.update_password(id, new_password)


@user_router.put("/{item_id}/password")
def update_password(password_change: ChangePassword, user_service: UserService = Depends(UserService.write_existing)):
    """Resets the User Password"""
    return user_service.change_password(password_change)


@public_router.post("/forgot-password")
def forgot_password(email: ForgotPassword, session: Session = Depends(generate_session)):
    """Sends an email with a reset link to the user"""
    f_service = PasswordResetService(session)
    return f_service.send_reset_email(email.email)


@public_router.post("/reset-password")
def reset_password(reset_password: ResetPassword, session: Session = Depends(generate_session)):
    """Resets the user password"""
    f_service = PasswordResetService(session)
    return f_service.reset_password(reset_password.token, reset_password.password)
