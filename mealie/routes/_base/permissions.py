from collections.abc import Callable
from enum import StrEnum
from typing import Any

from fastapi import Depends, HTTPException, status

from mealie.core.dependencies import get_current_user
from mealie.lang.providers import Translator, get_locale_provider
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


def _error(status_code: int, message: str | None) -> HTTPException:
    # The frontend shows `detail.message` as a toast, so a message is only sent when one is given.
    if message is None:
        return HTTPException(status_code)
    return HTTPException(status_code, detail=ErrorResponse.respond(message=message))


def forbidden(message: str | None = None) -> HTTPException:
    """The caller can see the resource but may not perform the action."""
    return _error(status.HTTP_403_FORBIDDEN, message)


def not_found(message: str | None = None) -> HTTPException:
    """The caller cannot see the resource. Use it for missing and inaccessible resources alike."""
    return _error(status.HTTP_404_NOT_FOUND, message)


class RequirePermission:
    """
    Route dependency that answers 403 unless the current user holds `perm`. The instance stays on the
    route's dependant, so the permission each route declares can be read back from `app.routes`.
    """

    def __init__(self, perm: Perm) -> None:
        self.perm = perm

    def __call__(
        self,
        user: PrivateUser = Depends(get_current_user),
        translator: Translator = Depends(get_locale_provider),
    ) -> None:
        if not _GRANTED_BY[self.perm](user):
            raise forbidden(translator.t("exceptions.permission-denied"))


def require(perm: Perm) -> Any:
    """Declare the permission a route needs: `@router.post("", dependencies=[require(Perm.GROUP_ORGANIZE)])`."""
    return Depends(RequirePermission(perm))
