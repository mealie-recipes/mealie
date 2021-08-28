from fastapi import Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.config import settings
from mealie.core.security import get_password_hash, verify_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.core.dependencies import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import ChangePassword, UserInDB

user_router = UserAPIRouter(prefix="")


@user_router.put("/{id}/reset-password")
async def reset_user_password(
    id: int,
    session: Session = Depends(generate_session),
):

    new_password = get_password_hash(settings.DEFAULT_PASSWORD)
    db.users.update_password(session, id, new_password)


@user_router.put("/{id}/password")
def update_password(
    id: int,
    password_change: ChangePassword,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Resets the User Password"""

    assert_user_change_allowed(id, current_user)
    match_passwords = verify_password(password_change.current_password, current_user.password)

    if not (match_passwords):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    new_password = get_password_hash(password_change.new_password)
    db.users.update_password(session, id, new_password)
