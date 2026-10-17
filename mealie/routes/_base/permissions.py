from collections.abc import Callable
from enum import StrEnum
from typing import Any

from fastapi import Depends, HTTPException, status

from mealie.core.dependencies import get_current_user
from mealie.schema.response import ErrorResponse
from mealie.schema.user.user import PrivateUser


class Perm(StrEnum):
    """
    A permission a route can require. The prefix names the scope the user flag applies to.
    `ANY_VALID_USER` marks a route as open to any signed-in user on purpose.
    """

    ANY_VALID_USER = "any_valid_user"
    GROUP_ORGANIZE = "group:organize"
    GROUP_MANAGE = "group:manage"
    GROUP_INVITE = "group:invite"
    HOUSEHOLD_MANAGE = "household:manage"


_GRANTED_BY: dict[Perm, Callable[[PrivateUser], bool]] = {
    Perm.ANY_VALID_USER: lambda _: True,
    Perm.GROUP_ORGANIZE: lambda user: user.can_organize,
    Perm.GROUP_MANAGE: lambda user: user.can_manage,
    Perm.HOUSEHOLD_MANAGE: lambda user: user.can_manage_household,
    Perm.GROUP_INVITE: lambda user: user.can_invite,
}


def forbidden() -> HTTPException:
    """The caller can see the resource but may not perform the action."""
    return HTTPException(status.HTTP_403_FORBIDDEN)


def not_found(message: str = "Not found.") -> HTTPException:
    """The caller cannot see the resource. Use it for missing and inaccessible resources alike."""
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond(message=message))


class RequirePermission:
    """
    Route dependency that answers 403 unless the current user holds `perm`. The instance stays on the
    route's dependant, so the permission each route declares can be read back from `app.routes`.
    """

    def __init__(self, perm: Perm) -> None:
        self.perm = perm

    def __call__(self, user: PrivateUser = Depends(get_current_user)) -> None:
        if not _GRANTED_BY[self.perm](user):
            raise forbidden()


def require(perm: Perm) -> Any:
    """Declare the permission a route needs: `@router.post("", dependencies=[require(Perm.GROUP_ORGANIZE)])`."""
    return Depends(RequirePermission(perm))
