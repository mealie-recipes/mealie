from fastapi import HTTPException, status

from mealie.schema.user.user import PrivateUser


def assert_user_change_allowed(id: int, current_user: PrivateUser):
    if current_user.id != id and not current_user.admin:
        # only admins can edit other users
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="NOT_AN_ADMIN")
