from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.core.config import settings
from mealie.core.security import hash_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.user import ChangePassword
from mealie.services.user.user_service import UserService

user_router = UserAPIRouter(prefix="")


@user_router.put("/{id}/reset-password")
async def reset_user_password(id: int, session: Session = Depends(generate_session)):
    new_password = hash_password(settings.DEFAULT_PASSWORD)
    db.users.update_password(session, id, new_password)


@user_router.put("/{id}/password")
def update_password(password_change: ChangePassword, user_service: UserService = Depends(UserService.write_existing)):
    """ Resets the User Password"""

    return user_service.change_password(password_change)
