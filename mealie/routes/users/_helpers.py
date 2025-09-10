from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.user import PrivateUser, UserBase

permission_attrs = ["can_invite", "can_manage", "can_manage_household", "can_organize", "admin"]


def _assert_non_admin_user_change_allowed(user_id: UUID4, current_user: PrivateUser, new_data: UserBase):
    if current_user.id != user_id:
        # User is trying to edit another user
        raise HTTPException(status.HTTP_403_FORBIDDEN, ErrorResponse.respond("User cannot edit other users"))

    if any(getattr(current_user, p) != getattr(new_data, p) for p in permission_attrs):
        # User is trying to change their own permissions
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            ErrorResponse.respond("User cannot change their own permissions"),
        )

    if current_user.group != new_data.group:
        # prevent a regular user from changing their group
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, ErrorResponse.respond("User doesn't have permission to change their group")
        )

    if current_user.household != new_data.household:
        # prevent a regular user from changing their household
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            ErrorResponse.respond("User doesn't have permission to change their household"),
        )


def assert_user_change_allowed(user_id: UUID4, current_user: PrivateUser, new_data: UserBase):
    if not current_user.admin:
        _assert_non_admin_user_change_allowed(user_id, current_user, new_data)
        return

    if current_user.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, ErrorResponse.respond("Use the Admin API to update other users"))

    # Admin is trying to edit themselves
    if any(getattr(current_user, p) != getattr(new_data, p) for p in permission_attrs):
        # prevent an admin from excalating their own permissions
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, ErrorResponse.respond("Admins can't change their own permissions")
        )
