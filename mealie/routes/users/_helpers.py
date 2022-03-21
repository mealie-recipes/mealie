from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.schema.user.user import PrivateUser


def assert_user_change_allowed(id: UUID4, current_user: PrivateUser):
    if current_user.id != id and not current_user.admin:
        # only admins can edit other users
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="NOT_AN_ADMIN")
